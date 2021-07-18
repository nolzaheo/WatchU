from flask import Flask

def create_app():
    app = Flask(__name__)

    # 블루프린트
    from views import socket_views
    app.register_blueprint(socket_views.bp)

    return app

if __name__ == '__main__':
    # create_app().run(host='172.30.1.47', port='8888', debug=True)
    create_app().run(host='172.30.1.7', port='8888', debug=True)
    # create_app().run(debug=True)