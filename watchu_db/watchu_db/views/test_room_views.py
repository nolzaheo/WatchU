import base64
from datetime import datetime
from tempfile import TemporaryFile

from flask import Blueprint, render_template, request, jsonify, g, url_for, Response
from werkzeug.datastructures import FileStorage
from werkzeug.utils import redirect

from watchu_db.models import Professor, TestRoom, Student, Log
from watchu_db import db
import secrets

from watchu_db.views import auth_views

bp = Blueprint('test_room', __name__, url_prefix='/test_room')


@bp.route('/', methods=["GET"])
@bp.route('/menu', methods=["GET"])
@auth_views.login_required
def menu():
    return render_template('test_room/menu.html')


@bp.route('/make', methods=["GET"])
@auth_views.login_required
def make():
    """ 시험 생성 """
    test_room_id = secrets.token_urlsafe(11)
    print(test_room_id)
    return render_template('test_room/make.html', test_room_id=test_room_id)


@bp.route('/make_ajax', methods=['GET', 'POST'])
def make_ajax():
    """ 시험 생성 정보 받기 & 데이터베이스 변경 """
    test_room_id = request.form['test_room_id']
    professor_id = request.form['professor_id']
    block_list = request.form['block_list']
    date = request.form['date'].split('-')
    start = request.form['start_time'].split(':')
    end = request.form['end_time'].split(':')
    start_date = datetime(int(date[0]), int(date[1]), int(date[2]), int(start[0]), int(start[1]))
    end_date = datetime(int(date[0]), int(date[1]), int(date[2]), int(end[0]), int(end[1]))

    # TestRoom 객체 생성
    test_room = TestRoom(
        id=test_room_id,
        professor=Professor.query.get(professor_id),
        block_list=block_list,
        start_date=start_date, end_date=end_date)
    db.session.add(test_room)

    # Student 객체 생성
    length = request.form['length']
    for i in range(int(length)):
        img = request.files[str(i)]
        student_id = img.filename[:8]
        image_data = img.read()
        student = Student(id=student_id, test_room_id=test_room_id, image=image_data)
        db.session.add(student)
    db.session.commit()
    return "Make Ajax Success"


@bp.route('/edit_list', methods=["GET"])
@auth_views.login_required
def edit_list():
    """ 수정 가능한 시험 리스트 """
    professor = Professor.query.get(g.user.id)
    test_room_list = []
    for t in professor.test_room_set:
        test_room_list.append(t.id)
    return render_template('test_room/edit_list.html', test_room_list=test_room_list)


@bp.route('/edit/<string:test_room_id>', methods=["GET"])
@auth_views.login_required
def edit(test_room_id):
    """ 시험 수정 """
    test_room = TestRoom.query.get(test_room_id)
    block_list = test_room.block_list.split(';')[:-1]
    start_date = str(test_room.start_date)
    end_date = str(test_room.end_date)
    date = start_date[0:10]
    start_time = start_date[11:16]
    end_time = end_date[11:16]
    student_list = []
    image_list = []
    for s in test_room.student_set:
        student_list.append(s.id)
        # python의 bytes를 javascript에서 그대로 못 읽어와서... base64 변환 적용
        img = base64.b64encode(s.image).decode()
        image_list.append(img)
    print(student_list)
    print(len(image_list))
    return render_template(f'test_room/edit.html', test_room_id=test_room_id, date=date, start_time=start_time,
                           end_time=end_time, block_list=block_list, student_list=student_list, image_list=image_list)


@bp.route('/edit_ajax', methods=['GET', 'POST'])
def edit_ajax():
    """ 시험 수정 정보 받기 & 데이터베이스 변경 """
    test_room_id = request.form['test_room_id']
    block_list = request.form['block_list']

    date = request.form['date'].split('-')
    start = request.form['start_time'].split(':')
    end = request.form['end_time'].split(':')
    start_date = datetime(int(date[0]), int(date[1]), int(date[2]), int(start[0]), int(start[1]))
    end_date = datetime(int(date[0]), int(date[1]), int(date[2]), int(end[0]), int(end[1]))

    # TestRoom 객체 수정
    test_room = TestRoom.query.get(test_room_id)
    test_room.block_list = block_list
    test_room.start_date = start_date
    test_room.end_date = end_date
    db.session.add(test_room)

    # Student 객체 수정 및 삭제
    length = request.form['length']
    for i in range(int(length)):
        img = request.files[str(i)]
        student_id = img.filename[:8]
        image_data = img.read()
        student = Student.query.filter(Student.id == student_id, Student.test_room_id == test_room_id).first()
        if student is not None:
            student.image = image_data
        else:
            student = Student(id=student_id, test_room_id=test_room_id, image=image_data)
        db.session.add(student)
    db.session.commit()
    return "Edit Ajax Success"


@bp.route('/delete/<string:test_room_id>', methods=["GET"])
def delete(test_room_id):
    """ 시험 삭제 """
    test_room = TestRoom.query.get(test_room_id)
    db.session.delete(test_room)
    db.session.commit()
    return redirect(url_for('test_room.edit_list'))


@bp.route('/watching_list', methods=["GET"])
@auth_views.login_required
def watching_list():
    """ 입장 가능 시험 리스트 """
    professor = Professor.query.get(g.user.id)
    test_room_list = []
    for t in professor.test_room_set:
        test_room_list.append(t.id)
    return render_template('test_room/watching_list.html', test_room_list=test_room_list)


image = open('./static/no_screen.png', 'rb').read()
images = dict()


def gen_frames(student_id):
    while True:
        # image = images[student_id]
        frame = bytearray(image)
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')


@bp.route('/<string:test_room_id>/<int:student_id>/screen_socket_feed')
def screen_socket_feed(test_room_id, student_id):
    return Response(gen_frames(student_id), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/watching/<string:test_room_id>', methods=["GET"])
@auth_views.login_required
def watching(test_room_id):
    """ 시험 중 화면 공유 """
    test_room = TestRoom.query.get(test_room_id)
    student_list = []
    for s in test_room.student_set:
        student_list.append(s.id)
        # images[s.id] = s.image # 임시로 학생 사진 넣기
    print(test_room_id, student_list)
    return render_template('test_room/watching.html', test_room_id=test_room_id, student_list=student_list)


@bp.route('/watching_detail/<string:test_room_id>/<int:student_id>')
def watching_detail(test_room_id, student_id):
    return render_template('test_room/watching_detail.html', test_room_id=test_room_id, student_id=student_id)
