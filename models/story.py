from db import db
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON

class Story(db.Model):
    __tablename__ = 'stories'
    id_story = db.Column(db.Integer, primary_key=True)
    story_code = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    sub_title = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to StoryContent
    contents = db.relationship('StoryContent', backref='story', lazy=True)


class StoryContent(db.Model):
    __tablename__ = 'story_contents'
    id_story_content = db.Column(db.Integer, primary_key=True)
    content_code = db.Column(db.String(50), unique=True, nullable=False)
    page_content = db.Column(JSON)

    # Foreign key to stories table
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id_story'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    quizzes = db.relationship('StoryQuiz', backref='story_content', lazy=True)

    
class StoryQuiz(db.Model):
    __tablename__ = 'story_quizzes'
    id_story_quiz = db.Column(db.Integer, primary_key=True)
    quiz_code = db.Column(db.String(50), unique=True, nullable=False)
    
    # Foreign key to story_content
    story_content_id = db.Column(db.Integer, db.ForeignKey('story_contents.id_story_content'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

   
