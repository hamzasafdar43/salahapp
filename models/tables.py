from db import db
from datetime import datetime












class StoryQuizAttempt(db.Model):
    __tablename__ = 'story_quiz_attempts'
    id_quiz_attempt = db.Column(db.Integer, primary_key=True)
    attempt_code = db.Column(db.String(50), unique=True, nullable=False)
    id_question = db.Column(db.Integer, db.ForeignKey('quiz_questions.id_question'), nullable=False)
    id_option_selected = db.Column(db.Integer, db.ForeignKey('question_options.id_option'), nullable=False)
    id_student = db.Column(db.Integer, db.ForeignKey('students.id_student'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    question = db.relationship("QuizQuestion")
    selected_option = db.relationship("QuestionOption")
    student = db.relationship("Student")
