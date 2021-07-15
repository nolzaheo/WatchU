from io import BytesIO

import cv2
from PIL import Image
from flask import Blueprint, render_template, send_file
from mss import mss
from numpy import asarray

bp = Blueprint('myscreen', __name__, url_prefix='/myscreen')

# 모니터의 스크린을 받아온다.
monitorId = 1
def getMonitor():
    global monitorId

    with mss() as sct:
        mon = sct.monitors[monitorId]

        # The screen part to capture
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "mon": monitorId
        }

        sct.compression_level = 2

        im_arr = asarray(sct.grab(monitor))

        im_arr = cv2.cvtColor(im_arr, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(im_arr)

        return img


# 스크린 이미지를 전송한다.
@bp.route('/myscreen/screen.png')
def serve_pil_image():
    img_buffer = BytesIO()
    img = getMonitor()
    img.save(img_buffer, 'PNG')
    img_buffer.seek(0)
    return send_file(img_buffer, mimetype='image/png')

@bp.route('/')
def myscreen():
    return render_template('test/myscreen.html')
