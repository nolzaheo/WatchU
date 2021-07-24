import json

from flask import Blueprint, render_template, request, jsonify
import secrets

bp = Blueprint('test_room', __name__, url_prefix='/test_room')

@bp.route('/')
@bp.route('/menu')
def menu():
    return render_template('test_room/menu.html')

@bp.route('/make')
def make():
    test_room_id = secrets.token_urlsafe(11)
    print(test_room_id)
    return render_template('test_room/make.html')

@bp.route('/upload_image', methods=["POST"])
def upload_image():
    if request.method == 'POST':
        images = request.files.getlist("images[]")
        print(images)
        for img in images:
            img.save('./images/' + img.filename)
            print(img.filename.split('.')[0])
        return render_template('test_room/menu.html')

@bp.route('/ajax', methods=["POST"])
def ajax():
    data = json.loads(request.data)
    block_list = data['block_list']
    image_name = data['student_list']
    image_list = data['image_list']
    print(data)
    print(block_list)
    print(image_name)
    # print(image_list)
    return "ajax"


