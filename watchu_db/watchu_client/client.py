import socket
from mss import mss, tools

clientSocket = socket.socket()
# clientSocket.connect(('172.30.1.30', 8888))
clientSocket.connect(("192.168.43.233", 7777))

test_room_id = "fZKBi-0Y2bfSrPY"
student_id = 20190327

def getScreen():
    with mss() as sct:
        mon = sct.monitors[1]
        rect = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "mon": 1
        }

        clientSocket.send(test_room_id.encode('utf-8'))
        clientSocket.send(student_id.to_bytes(1024, 'big'))

        while True:
            # Capture the screen
            im = sct.grab(rect)
            pixels = tools.to_png(im.rgb, im.size)

            # Send the size of the pixels length
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            clientSocket.send(bytes([size_len]))

            # Send the actual pixels length
            size_bytes = size.to_bytes(size_len, 'big')
            clientSocket.send(size_bytes)

            # Send pixels
            clientSocket.sendall(pixels)

getScreen()