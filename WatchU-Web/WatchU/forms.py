from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField
from wtforms.validators import DataRequired, EqualTo


class ProfessorCreateForm(FlaskForm):
    id = IntegerField('교수번호', validators=[DataRequired('교수번호를 입력해주세요.')])
    password1 = PasswordField('비밀번호', validators=[
        DataRequired('비밀번호를 입력해주세요.'), EqualTo('password2', '비밀번호가 일치하지 않습니다')])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired('비밀번호를 입력해주세요.')])


class ProfessorLoginForm(FlaskForm):
    id = IntegerField('교수번호', validators=[DataRequired('교수번호를 입력해주세요.')])
    password = PasswordField('비밀번호', validators=[DataRequired('비밀번호를 입력해주세요.')])