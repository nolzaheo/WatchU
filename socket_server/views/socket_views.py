
import base64
from flask import Blueprint, render_template, request, Response, url_for
from werkzeug.utils import redirect

bp = Blueprint('socket', __name__, url_prefix='/')

image = open('./static/no_screen.png', 'rb').read()
images = dict()
images[19970327] = image
images[19970217] = image
student_cnt=2 #DB에서 학생 수 가져와야함

import socket
import threading

def recvall(conn, length):
    """ Retreive all pixels. """
    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def receive(sock,student_id):
     while True:
            size_len = int.from_bytes(sock.recv(1), byteorder='big')
            size = int.from_bytes(sock.recv(size_len), byteorder='big')
            image = recvall(sock, size)
            if len(image) != 0:
                images[student_id] = image


def open_socket():
    serverSock = socket.socket()
    serverSock.bind(('172.30.1.30', 8888))
    try:
        print("Listening ....")
        serverSock.listen(student_cnt)
        for _ in range(student_cnt):
            connectionSock, addr = serverSock.accept()
            print("Accepted ....", addr)
            student_id = int.from_bytes(connectionSock.recv(1024), byteorder='big')
            receiver = threading.Thread(target=receive, args=(connectionSock,student_id))
            receiver.start()
    finally:
        serverSock.close()

def gen_frames(student_id):
    while True:
        image = images[student_id]
        frame = bytearray(image)
        yield (b'--frame\r\n'
                b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@bp.route('/')
def screen_socket():
    th = threading.Thread(target=open_socket)
    th.start()
    return render_template('/index.html')

@bp.route('/<int:testroom_id>/<int:student_id>/screen_socket_feed')
def screen_socket_feed(testroom_id, student_id):
    return Response(gen_frames(student_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/')
def home():
    return redirect(url_for('socket.screen_socket'))
