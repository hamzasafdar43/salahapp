from flask import request, jsonify
from db import app, db
from models.user import Student


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Generate student_code automatically
    last_student = Student.query.order_by(Student.id_student.desc()).first()
    next_id = 1 if not last_student else last_student.id_student + 1
    student_code = f"STU{str(next_id).zfill(4)}"  # STU0001, STU0002, ...

    # Check if email already exists (optional)
    if Student.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Save new student
    student = Student(
        student_code=student_code,
        name=data['name'],
        email=data['email'],
        password=data['password']
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({'message': 'Student registered successfully', 'student_code': student_code}), 201



@app.route('/users', methods=['GET'])
def get_users():
    users = Student.query.all()
    return jsonify([
        {
            'id': u.id_student,
            'name': u.name,
            'email': u.email
        } for u in users
    ]), 200

