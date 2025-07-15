from db import app, db
from routes import users                          
from routes.story import story_bp               

app.register_blueprint(story_bp)               

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all() 
        db.create_all()
    app.run(debug=True)
