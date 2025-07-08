from db import app, db

# Import your routes to register them
from routes import users  # make sure this file registers the routes

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
