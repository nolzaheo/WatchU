from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from watchu import db
from watchu.forms import UserCreateForm, ProfessorLoginForm
from watchu.models import Professor

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup_professor/', methods=('GET', 'POST'))
def signup_professor():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = Professor.query.filter_by(username=form.username.data).first()
        if not user:
            user = Professor(
                username=form.username.data,
                password=generate_password_hash(form.password1.data)
            )
            db.session.add(user)
            db.session.commit()
            # 회원가입 완료 후 로그인 페이지로 이동
            return redirect(url_for('auth.login_professor'))
        else:
            flash('이미 존재하는 사용자입니다.')

    # 'GET'일 경우 회원가입 페이지로 이동
    # 회원가입 실패 시 다시 회원가입 페이지로 이동
    return render_template('/auth/signup_professor.html', form=form)


@bp.route('/')
def login():
    return render_template('/auth/login_professor.html')


@bp.route('/login_professor/', methods=('GET', 'POST'))
def login_professor():
    form = ProfessorLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = Professor.query.filter_by(username=form.username.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('testroom.menu'))
        flash(error)
    return render_template('auth/login_professor.html', form=form)

@bp.before_app_request
def load_logged_in_professor():
    professor_id = session.get('user_id')
    if professor_id is None:
        g.user = None
    else:
        g.user = Professor.query.get(professor_id)

@bp.route('/logout_professor/')
def logout_professor():
    session.clear()
    return redirect(url_for('main.home')) # auth/login_professor로 변경해야함
