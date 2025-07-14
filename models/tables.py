from db import db
from datetime import datetime






class StoryContent(db.Model):
    __tablename__ = 'story_contents'
    id_story_content = db.Column(db.Integer, primary_key=True)
    content_code = db.Column(db.String(50), unique=True, nullable=False)
    page_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StoryQuiz(db.Model):
    __tablename__ = 'story_quizzes'
    id_story_quiz = db.Column(db.Integer, primary_key=True)
    quiz_code = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    id_question = db.Column(db.Integer, primary_key=True)
    question_code = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    id_story_quiz = db.Column(db.Integer, db.ForeignKey('story_quizzes.id_story_quiz'), nullable=False)
    id_option_correct = db.Column(db.Integer, db.ForeignKey('question_options.id_option'), nullable=True)
    coins = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    story_quiz = db.relationship("StoryQuiz", backref="questions")
    correct_option = db.relationship("QuestionOption", foreign_keys=[id_option_correct])

class QuestionOption(db.Model):
    __tablename__ = 'question_options'
    id_option = db.Column(db.Integer, primary_key=True)
    option_code = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.String(255), nullable=False)
    id_question = db.Column(db.Integer, db.ForeignKey('quiz_questions.id_question'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    question = db.relationship("QuizQuestion", backref="options")

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
