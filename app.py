
from flask import Flask
from db import db  # Import db from separate file
from routes.story import story_bp

app = Flask(__name__)
<<<<<<< HEAD
=======
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Hamza%40123@localhost/testdb'
>>>>>>> 938318d (update models and api json)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://alihamza43:Hamza%40123@alihamza43.mysql.pythonanywhere-services.com/alihamza43$default'  # Or your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db with the app

app.register_blueprint(story_bp)


with app.app_context():
    # db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)



