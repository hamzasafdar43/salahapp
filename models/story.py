from db import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import JSON

class Story(db.Model):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    storyName = Column(String(100), nullable=False)
    quize = Column(JSON)  # List of question-answer pairs
    getcoin = Column(Integer)

class StoriesData(db.Model):
    __tablename__  = "storiesData"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    key = db.Column(db.String(50), unique=True)
    subtitle = db.Column(db.String(200))
    pages = db.Column(db.PickleType)
    audio_files = db.Column(db.PickleType)

class StoryQuiz(db.Model):
    __tablename__ = 'storiesQuiz'  

    id = db.Column(db.Integer, primary_key=True)
    story_key = db.Column(db.String(100), unique=True, nullable=False)
    quiz_data = db.Column(db.PickleType, nullable=False)