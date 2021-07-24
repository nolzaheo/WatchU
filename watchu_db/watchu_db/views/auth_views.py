from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from watchu_db import db
from watchu_db.forms import ProfessorCreateForm, ProfessorLoginForm
from watchu_db.models import Professor

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/')
def login():
    return render_template('/auth/login_professor.html')

@bp.route('/signup_professor/', methods=('GET', 'POST'))
def signup_professor():
    ''' 교수 회원가입 '''
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

@bp.route('/login_professor/', methods=('GET', 'POST'))
def login_professor():
    ''' 교수 로그인'''
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

@bp.before_app_request
def load_logged_in_professor():
    professor_id = session.get('professor_id')
    if professor_id is None:
        g.user = None
    else:
        g.user = Professor.query.get(professor_id)

@bp.route('/logout_professor/')
def logout_professor():
    ''' 교수 로그아웃 '''
    session.clear()
    return redirect(url_for('auth.login_professor'))
