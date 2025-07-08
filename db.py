from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Update with your actual MySQL credentials and DB name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Hamza%40123@localhost/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)