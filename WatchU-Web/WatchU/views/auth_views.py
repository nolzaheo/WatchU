import functools
from flask import Blueprint, url_for, render_template, flash, request, session, g, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from WatchU import db
from WatchU.forms import ProfessorCreateForm, ProfessorLoginForm
from WatchU.models import Professor

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """ 로그인 여부 확인 데코레이터 (로그인전) """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login_professor'))
        return view(**kwargs)

    return wrapped_view


def login_not_required(view):
    """ 로그인 여부 확인 데코레이터 (로그인후) """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is not None:
            return redirect(url_for('test_room.menu'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/login_professor/', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
@login_not_required
def login_professor():
    """ 교수 로그인 """
    form = ProfessorLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        professor = Professor.query.filter_by(id=form.id.data).first()
        if not professor:
            error = "등록되지 않는 교수입니다."
        elif not check_password_hash(professor.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['professor_id'] = professor.id
            return redirect(url_for('test_room.menu'))
        flash(error)
    return render_template('auth/login_professor.html', form=form)


@bp.route('/signup_professor/', methods=['GET', 'POST'])
@login_not_required
def signup_professor():
    """ 교수 회원가입 """
    form = ProfessorCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        professor = Professor.query.filter_by(id=form.id.data).first()
        if not professor:
            professor = Professor(
                id=form.id.data,
                password=generate_password_hash(form.password1.data)
            )
            db.session.add(professor)
            db.session.commit()
            return redirect(url_for('auth.login_professor'))
        else:
            flash('이미 존재하는 교수입니다.')
    return render_template('/auth/signup_professor.html', form=form)


@bp.before_app_request
def load_logged_in_professor():
    professor_id = session.get('professor_id')
    if professor_id is None:
        g.user = None
    else:
        g.user = Professor.query.get(professor_id)


@bp.route('/logout_professor/')
def logout_professor():
    """ 교수 로그아웃 """
    session.clear()
    return redirect(url_for('auth.login_professor'))


@bp.route('/student_exe_download')
def student_exe_download():
    """ 학생 프로그램 다운로드 """
    file_name = f"student_exe/student.exe"
    return send_file(file_name, as_attachment=True)