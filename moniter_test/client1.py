import base64
import requests
from mss import mss, tools

WIDTH = 1900
HEIGHT = 1000

testroom_id = 1
student_id = 19970327

def getScreen():
    with mss() as sct:
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while True:
            sct.compression_level = 2
            im = sct.grab(rect)
            image_byte = tools.to_png(im.rgb, im.size)

            body = {
                "image": base64.b64encode(image_byte).decode()
            }

            # res = requests.post(f'http://127.0.0.1:5000/image/{testroom_id}/{student_id}/json', json=body)
            # res = requests.post(f'http://172.30.1.47:8888/image/{testroom_id}/{student_id}/json', json=body)
            res = requests.post(f'http://172.30.1.7:8888/image/{testroom_id}/{student_id}/json', json=body)



getScreen()
