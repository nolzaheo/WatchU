import os

# SQLAlchemy Setting
BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'watchu_db.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-WTF Setting
SECRET_KEY = "eAGcOCztg807B7CZB6Y1oiAB_6-0wgUOQUA7w1VDLBU"