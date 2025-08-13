from flask import Blueprint, request, jsonify
from db import db
from models.user import Student
from models.story import StoryReward , StoryQuizAttempt

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



@users.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    student = Student.query.filter_by(email=email).first()

    if not student or student.password != password:
        return jsonify({'error': 'Invalid email or password'}), 401

    return jsonify({
        'message': 'Login successful',
        'student': {
            'id': student.id_student,
            'student_code': student.student_code,
            'name': student.name,
            'email': student.email
        }
    }), 200


@users.route('/students', methods=['GET'])
def get_all_students():
    students = Student.query.all()

    students_list = []
    for s in students:
        students_list.append({
            'id_student': s.id_student,
            'student_code': s.student_code,
            'name': s.name,
            'email': s.email,
            'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': s.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify(students_list), 200


@users.route('/delete_student/<string:student_code>', methods=['DELETE'])
def delete_student(student_code):
    
    student = Student.query.filter_by(student_code=student_code).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    try:

        StoryReward.query.filter_by(student_code=student_code).delete()

        StoryQuizAttempt.query.filter_by(id_student=student.id_student).delete()

        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": f"Student '{student_code}' and related data deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500