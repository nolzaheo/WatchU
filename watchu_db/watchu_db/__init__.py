import io
import threading
import socket

from PIL import Image
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

# =========================== Screen Socket ============================
no_screen_image = open('./static/no_screen.png', 'rb').read()
global_images = dict()  # 전체 화면 공유 이미지 저장 딕셔너리
def open_socket():
    global global_images
    from watchu_db.models import TestRoom
    from watchu_db import db
    serverSock = socket.socket()
    # serverSock.bind(('172.30.1.30', 8888))
    serverSock.bind(('172.30.1.2', 7777))
    try:
        print("Listening ....")
        serverSock.listen(100)
        while True:
            connectionSock, addr = serverSock.accept()
            print("Accepted ....", addr)
            test_room_id = str(connectionSock.recv(15).decode('utf-8'))
            student_id = int.from_bytes(connectionSock.recv(1024), byteorder='big')
            print(test_room_id, student_id)
            global_images[test_room_id] = dict()
            test_room = TestRoom.query.get(test_room_id)
            images = dict()
            for s in test_room.student_set:
                images[s.id] = no_screen_image
                # images[s.id] = s.image # 임시로 학생 사진 넣기
            # student_cnt = len(student_list)
            global_images[test_room_id] = images
            print(test_room_id)
            receiver = threading.Thread(target=receive, args=(connectionSock, test_room_id, student_id))
            receiver.start()
    finally:
        serverSock.close()

def recvall(conn, length):
    """ Retreive all pixels. """
    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def receive(sock, test_room_id, student_id):
    while True:
        size_len = int.from_bytes(sock.recv(1), byteorder='big')
        size = int.from_bytes(sock.recv(size_len), byteorder='big')
        image = recvall(sock, size)
        if len(image) != 0:
            global_images[test_room_id][student_id] = image
            img = Image.open(io.BytesIO(global_images[test_room_id][student_id]))
            img.save("MyTest.png")
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
    from watchu_db import models
# ======================================================================

    # 블루프린트
    from watchu_db.views import main_views, auth_views, test_room_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(test_room_views.bp)

    # 화면 공유 소켓
    th = threading.Thread(target=open_socket)
    th.start()
    return app

if __name__ == '__main__':
    # create_app().run(debug=True)
    create_app().run(host="172.30.1.2", port=5000, debug=True)
    # create_app().run(host="10.23.48.49", port=5000, debug=True)
    # create_app().run(host="192.168.43.233", port=5000, debug=True)