from flask import Blueprint, url_for, render_template
from werkzeug.utils import redirect

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def home():
    return redirect(url_for('auth.login_professor'))

@bp.route('/help')
def help():
    return render_template('help.html')