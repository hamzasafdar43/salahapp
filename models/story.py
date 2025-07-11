from db import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import JSON

class Story(db.Model):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    storyName = Column(String(100), nullable=False)
    quize = Column(JSON)  # List of question-answer pairs
    getcoin = Column(Integer)
