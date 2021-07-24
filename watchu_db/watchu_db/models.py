from watchu_db import db

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String, nullable=False)

class TestRoom(db.Model):
    id = db.Column(db.String, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id', ondelete='CASCADE'), nullable=False)
    professor = db.relationship('Professor', backref=db.backref('test_room_set', cascade='all, delete-orphan'))
    block_list = db.Column(db.String, nullable=False)
    start_date = db.Column(db.DateTime(), nullable=False)
    end_date = db.Column(db.DateTime(), nullable=False)

class Student(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, nullable=False)
    test_room_id = db.Column(db.String, db.ForeignKey('test_room.id', ondelete='CASCADE'), nullable=False)
    test_room = db.relationship('TestRoom', backref=db.backref('student_set', cascade='all, delete-orphan'))
    image = db.Column(db.LargeBinary, nullable=False)

class Log(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    # test_room_id = db.Column(db.String, db.ForeignKey('test_room.id', ondelete='CASCADE'), nullable=False)
    # test_room = db.relationship('TestRoom', backref=db.backref('log_set', cascade='all, delete-orphan'))
    student_index = db.Column(db.Integer, db.ForeignKey('student.index', ondelete='CASCADE'), nullable=False)
    student = db.relationship('Student', backref=db.backref('log_set', cascade='all, delete-orphan'))
    type = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)
