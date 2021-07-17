import socket
from mss import mss, tools

clientSocket = socket.socket()
# clientSocket.connect(('172.30.1.47', 8080))
clientSocket.connect(('172.30.1.7:8888', 8080))

WIDTH = 1900
HEIGHT = 1000

testroom_id = 1
student_id = 19970217

def getScreen():
    with mss() as sct:
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while True:
            sct.compression_level = 2
            im = sct.grab(rect)
            image_byte = tools.to_png(im.rgb, im.size)
            image = image_byte

            clientSocket.send(str(student_id).encode('utf-8'))
            clientSocket.send(image)

getScreen()
