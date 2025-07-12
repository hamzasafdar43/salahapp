from flask import Flask
from db import db
from routes.story import story_bp

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://alihamza43:Hamza%40123@alihamza43.mysql.pythonanywhere-services.com/alihamza43$default'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Hamza%40123@localhost/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(story_bp)


if __name__ == '__main__':
    app.run(debug=True)
