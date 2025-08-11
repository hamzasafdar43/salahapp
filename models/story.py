from db import db
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON


class Story(db.Model):
    __tablename__ = "stories"
    id_story = db.Column(db.Integer, primary_key=True)
    story_code = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    sub_title = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contents = db.relationship(
        "StoryContent",
        backref="story",
        lazy=True,
        foreign_keys="[StoryContent.story_id]",
        primaryjoin="Story.id_story == StoryContent.story_id"
    )


class StoryContent(db.Model):
    __tablename__ = "story_contents"
    id_story_content = db.Column(db.Integer, primary_key=True)
    content_code = db.Column(db.String(50), unique=True, nullable=False)
    page_content = db.Column(db.JSON)
    story_id = db.Column(
        db.Integer, db.ForeignKey("stories.id_story"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StoryQuiz(db.Model):
    __tablename__ = "story_quizzes"
    id_story_quiz = db.Column(db.Integer, primary_key=True)
    quiz_code = db.Column(db.String(50), unique=True, nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey("stories.id_story"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = db.relationship("QuizQuestion", backref="quiz", lazy=True)


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id_question = db.Column(db.Integer, primary_key=True)
    question_code = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    quiz_code = db.Column(db.String(50), db.ForeignKey("story_quizzes.quiz_code"), nullable=False)
    correct_option_content = db.Column(db.String(255), nullable=True) 
    coins = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    options = db.relationship("QuestionOption", backref="question", lazy=True)


class QuestionOption(db.Model):
    __tablename__ = "question_options"

    id_option = db.Column(db.Integer, primary_key=True)
    option_code = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.String(255), nullable=False)

    
    id_question = db.Column(db.Integer, db.ForeignKey("quiz_questions.id_question"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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


class StoryReward(db.Model):
    __tablename__ = 'story_reward'
    id_story_reward = db.Column(db.Integer, primary_key=True)
    reward_code = db.Column(db.String(50), unique=True, nullable=False)
    id_story = db.Column(db.Integer, db.ForeignKey('stories.id_story'), nullable=False)  # <-- here!
    coins_required = db.Column(db.Integer, nullable=False)
    is_locked = db.Column(db.Boolean, default=True)
    reward_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    story = db.relationship('Story', backref=db.backref('rewards', lazy=True))
