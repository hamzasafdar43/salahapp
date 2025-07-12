from app import app, db
from models.story import StoryQuiz

with app.app_context():
    db.create_all()
    print("Tables created!")
