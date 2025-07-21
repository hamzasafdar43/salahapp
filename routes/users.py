from flask import Blueprint, request, jsonify
from db import db
from models.user import Student

users = Blueprint('users', __name__)

@users.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    last_student = Student.query.order_by(Student.id_student.desc()).first()
    next_id = 1 if not last_student else last_student.id_student + 1
    student_code = f"STU{str(next_id).zfill(4)}"

    if Student.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    student = Student(
        student_code=student_code,
        name=data['name'],
        email=data['email'],
        password=data['password']
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({'message': 'Student registered successfully', 'student_code': student_code}), 201

@users.route('/users', methods=['GET'])
def get_users():
    users_list = Student.query.all()
    return jsonify([
        {
            'id': u.id_student,
            'name': u.name,
            'email': u.email
        } for u in users_list
    ]), 200
