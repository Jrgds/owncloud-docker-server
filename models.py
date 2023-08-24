from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

def user_exists(username):  # Ajout de la définition de user_exists
    return User.query.filter_by(username=username).first() is not None
