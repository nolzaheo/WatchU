import socket
from mss import mss, tools

clientSocket = socket.socket()
clientSocket.connect(('172.30.1.30', 8888))

testroom_id = 1
student_id = 19970327

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