from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Связь многие-ко-многим для студентов и групп
student_group = db.Table('student_group',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    
    # Отношения
    attendances = db.relationship('Attendance', backref='student', lazy='dynamic')
    grades = db.relationship('Grade', backref='student', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    faculty = db.Column(db.String(64))
    year = db.Column(db.Integer)
    
    # Отношения
    students = db.relationship('User', 
                              secondary=student_group,
                              lazy='subquery',
                              backref=db.backref('groups', lazy=True))
    schedules = db.relationship('Schedule', backref='group', lazy='dynamic')
    
    def __repr__(self):
        return f'<Group {self.name}>'

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    
    # Отношения
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    teacher = db.relationship('User', backref='subjects')
    schedules = db.relationship('Schedule', backref='subject', lazy='dynamic')
    grades = db.relationship('Grade', backref='subject', lazy='dynamic')
    
    def __repr__(self):
        return f'<Subject {self.name}>'

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 (понедельник-воскресенье)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(20))
    
    # Отношения
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    attendances = db.relationship('Attendance', backref='schedule', lazy='dynamic')
    
    def __repr__(self):
        return f'<Schedule {self.subject.name} {self.day_of_week} {self.start_time}>'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Boolean, default=False)  # True - присутствовал, False - отсутствовал
    
    # Отношения
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    
    def __repr__(self):
        return f'<Attendance {self.student.username} {self.date} {self.status}>'

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # Значение оценки
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    comment = db.Column(db.Text)
    
    # Отношения
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    def __repr__(self):
        return f'<Grade {self.student.username} {self.subject.name} {self.value}>'