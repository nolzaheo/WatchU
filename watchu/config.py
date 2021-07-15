import os

# SQLAlchemy Setting
BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'watchu.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-WTF Setting
SECRET_KEY = "watchu"