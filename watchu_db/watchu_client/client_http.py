import base64
import requests
from mss import mss, tools

test_room_id = "fZKBi-0Y2bfSrPY"
student_id = 20150113

def getScreen():
    with mss() as sct:
        # 화면 사이즈 받아옴
        mon = sct.monitors[1]
        rect = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "mon": 1
        }

        while True:
            # 화면 캡쳐
            im = sct.grab(rect)
            image_byte = tools.to_png(im.rgb, im.size)

            data = {
                "image": base64.b64encode(image_byte).decode()
            }

            # HTTP로 화면 이미지 전송
            res = requests.post(f'http://127.0.0.1:5000/test_room/share_screen/{test_room_id}/{student_id}', data=data)

getScreen()