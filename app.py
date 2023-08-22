from flask import Flask, request
import requests
import base64
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

OWNCLOUD_API_URL = "http://localhost:8080/ocs/v1.php/cloud/users"
ADMIN_CREDENTIALS = "admin:admin"

@app.route('/register', methods=['POST'])
def register_user():
    username = request.form.get("username")
    password = request.form.get("password")

    if user_exists(username):
        return "L'utilisateur existe déjà."

    user_data = {
        "userid": username,
        "password": password,
        "groups": ["Everyone"]
    }

    headers = {
        "Authorization": "Basic " + base64.b64encode(ADMIN_CREDENTIALS.encode()).decode()
    }

    response = requests.post(OWNCLOUD_API_URL, data=user_data, headers=headers)

    if response.ok:
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        return "Utilisateur enregistré avec succès !"
    else:
        return f"Échec de l'enregistrement de l'utilisateur. Code de statut : {response.status_code}"

def user_exists(username):
    return User.query.filter_by(username=username).first() is not None

if __name__ == '__main__':
    db.create_all()  # Créer les tables dans la base de données si elles n'existent pas déjà
    app.run(debug=True, host='0.0.0.0', port=5000)
