from flask import Blueprint, render_template

bp = Blueprint('testroom', __name__, url_prefix='/testroom')

@bp.route('/menu')
def menu():
    return render_template('testroom/menu.html')