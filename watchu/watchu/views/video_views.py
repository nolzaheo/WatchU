from flask import Blueprint, Response, render_template

bp = Blueprint('video', __name__, url_prefix='/video')

# 웹캠
import cv2

camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@bp.route('/')
def video():
    return render_template('test/video.html')

@bp.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')