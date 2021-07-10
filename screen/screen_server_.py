# 서버에게 클라이언트의 스크린을 공유
# 서버 : 클라이언트로부터 스크린을 받아 화면에 보여준다.
# 현재 한명의 client와 연결 가능
# thread로 실행시킨다.

import socket
from threading import Thread
from zlib import decompress

import pygame

WIDTH = 1900
HEIGHT = 1000


def recvall(conn, length):
    """ Retreive all pixels. """
    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def recv_thread(conn, screen, clock):
    # Retreive the size of the pixels length, the pixels length and pixels
    size_len = int.from_bytes(conn.recv(1), byteorder='big')
    size = int.from_bytes(conn.recv(size_len), byteorder='big')
    pixels = decompress(recvall(conn, size))

    # Create the Surface from raw pixels
    img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

    # Display the picture
    screen.blit(img, (0, 0))
    pygame.display.flip()
    clock.tick(60)


def main(host='127.0.0.1', port=6969):
    ''' machine lhost'''
    sock = socket.socket()
    sock.bind((host, port))
    print("Listening ....")
    sock.listen(5)
    conn, addr = sock.accept()
    print("Accepted ....", addr)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    watching = True

    try:
        while watching:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break
            thread = Thread(target=recv_thread, args=(conn, screen, clock,))
            thread.start()

    finally:
        sock.close()



if __name__ == "__main__":
    main()