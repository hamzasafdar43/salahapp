from flask import Flask
from db import db  # db imported from db.py
from routes.story import story_bp
from routes.users import users



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Hamza%40123@localhost/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Properly initialize db here

app.register_blueprint(story_bp)
app.register_blueprint(users)

with app.app_context():
    # db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
