from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
import requests
import base64
import re
import configparser

app = Flask(__name__)

# Charger les informations d'identification depuis le fichier de configuration
config = configparser.ConfigParser()
config.read('config.ini')

ADMIN_CREDENTIALS = f"{config['Credentials']['username']}:{config['Credentials']['password']}"
OWNCLOUD_API_URL = "http://localhost:8080/ocs/v1.php/cloud/users"

# Configurer la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Modèle pour la table des utilisateurs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

@app.route('/register', methods=['POST'])
def register_user():
    # Obtenez les informations du formulaire
    username = request.form.get("username")
    password = request.form.get("password")

    # Vérifiez si l'utilisateur existe déjà dans la base de données
    if user_exists(username):
        return "L'utilisateur existe déjà."

    # Enregistrez l'utilisateur dans la base de données
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()

    return "Utilisateur enregistré avec succès !"

# Fonction pour vérifier si un utilisateur existe déjà dans la base de données
def user_exists(username):
    user = User.query.filter_by(username=username).first()
    return user is not None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Créer les tables dans la base de données si elles n'existent pas déjà
    app.run(debug=True, host='0.0.0.0', port=5000)
