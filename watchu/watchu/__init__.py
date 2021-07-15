from flask import Flask

# ================================= DB =================================
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import MetaData

import config

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
# ======================================================================

def create_app():
    app = Flask(__name__)

# ================================= DB =================================
    app.config.from_object(config)

    # ORM
    db.init_app(app)
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
    from watchu import models
# ======================================================================

    # 블루프린트
    from watchu.views import main_views, auth_views, testroom_views, video_views, myscreen_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(testroom_views.bp)
    app.register_blueprint(video_views.bp)
    app.register_blueprint(myscreen_views.bp)

    return app

if __name__ == '__main__':
    #create_app().run(host='172.30.50.228', port='8888', debug=True)
    create_app().run(debug=True)
