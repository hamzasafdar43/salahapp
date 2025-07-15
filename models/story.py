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
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    contents = db.relationship(
        "StoryContent",
        backref="story",
        lazy=True,
        primaryjoin="Story.story_code==StoryContent.story_code",
    )


class StoryContent(db.Model):
    __tablename__ = "story_contents"
    id_story_content = db.Column(db.Integer, primary_key=True)
    content_code = db.Column(db.String(50), unique=True, nullable=False)
    page_content = db.Column(JSON)
    story_code = db.Column(
        db.String(50), db.ForeignKey("stories.story_code"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    quizzes = db.relationship(
        "StoryQuiz",
        backref="story_content",
        lazy=True,
        primaryjoin="StoryContent.content_code==StoryQuiz.story_content_code",
    )


class StoryQuiz(db.Model):
    __tablename__ = "story_quizzes"
    id_story_quiz = db.Column(db.Integer, primary_key=True)
    quiz_code = db.Column(db.String(50), unique=True, nullable=False)
    story_content_code = db.Column(
        db.String(50), db.ForeignKey("story_contents.content_code"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id_question = db.Column(db.Integer, primary_key=True)
    question_code = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    quiz_code = db.Column(db.String(50), db.ForeignKey("story_quizzes.quiz_code"), nullable=False)
    correct_option_code = db.Column(db.String(50), nullable=True)  

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    options = db.relationship("QuestionOption", backref="question", lazy=True)


class QuestionOption(db.Model):
    __tablename__ = 'question_options'

    id_option = db.Column(db.Integer, primary_key=True)
    option_code = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.String(255), nullable=False)
    question_code = db.Column(db.String(50), db.ForeignKey('quiz_questions.question_code'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
