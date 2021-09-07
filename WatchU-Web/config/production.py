from config.default import *

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'WatchU.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "eAGcOCztg807B7CZB6Y1oiAB_6-0wgUOQUA7w1VDLBU"