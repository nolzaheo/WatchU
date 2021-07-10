# 스키마 변경 후
# 1. flask db migrate
# 2. flask db upgrade

from watchu import db

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
