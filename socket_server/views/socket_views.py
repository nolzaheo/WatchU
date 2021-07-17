import base64
from flask import Blueprint, render_template, request, Response, url_for
from werkzeug.utils import redirect

bp = Blueprint('socket', __name__, url_prefix='/')

image = open('./static/no_screen.png', 'rb').read()
images = dict()
images[19970327] = image
images[19970217] = image

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

def receive(sock):
    while True:
        # student_id = int(sock.recv(1024).decode('utf-8'))
        # image_size = int(sock.recv(1024).decode('utf-8'))

        # student_id_len = int.from_bytes(sock.recv(1), byteorder='big')
        # image_size = int.from_bytes(sock.recv(1), byteorder='big')
        # print(image_size)
        # image = sock.recv(image_size)
        # if len(image) != 0:
        #     images[student_id] = image

        student_id = int.from_bytes(sock.recv(1024), byteorder='big')
        # print(f"student_id = {student_id}")
        size_len = int.from_bytes(sock.recv(1), byteorder='big')
        # print(f"size_len = {size_len}")
        size = int.from_bytes(sock.recv(size_len), byteorder='big')
        # print(f"size = {size}")
        image = recvall(sock, size)
        # print(image)
        if len(image) != 0:
            images[student_id] = image


def open_socket():
    serverSock = socket.socket()
    # serverSock.bind(('172.30.1.47', 8080))
    serverSock.bind(('172.30.1.7', 8080))
    try:
        print("Listening ....")
        serverSock.listen(2)
        while True:
            connectionSock, addr = serverSock.accept()
            print("Accepted ....", addr)
            receiver = threading.Thread(target=receive, args=(connectionSock,))
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