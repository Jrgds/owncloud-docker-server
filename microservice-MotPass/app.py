from flask import Flask, request, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import base64
import re
import configparser
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Charger les informations d'identification depuis le fichier de configuration "config.ini"
config = configparser.ConfigParser()
config.read('config.ini')

admin_credentials = config.get('Credentials', 'ADMIN_CREDENTIALS')
OWNCLOUD_API_URL = "http://localhost:8080/ocs/v1.php/cloud/users"

# Configurer la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Modèle pour la table des utilisateurs
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Changez le type d'argument user_id en string dans la route
@app.route('/update/<string:user_id>', methods=['PUT'])
def update_password(user_id):
    print(request.json.get('new_password'))
    try:
        if user_exists(user_id) and owncloud_user_exists(user_id):  # Vérifiez si l'utilisateur existe
            print(f"Received request to update password for user: {user_id}")
            user = Users.query.filter_by(username=user_id).first()
            print(f"Received request to update password for user: {user}")

            new_password = request.json.get('new_password')
            print('Nouveau mot de pass: {new_password}')
            
            group_data = {
                "key": "password",
                "value": new_password
            }

            headers = {
            "Authorization": "Basic " + base64.b64encode(admin_credentials.encode()).decode()
            }

            response = requests.put(f"{OWNCLOUD_API_URL}/{user_id}", data=group_data, headers=headers)
            
            if response:
                user.password = new_password # Utilisation de la variable "user" pour la mise à jour sur le serveur OwnCloud
                db.session.commit()  
                return "Mot de passe mis à jour"
            else:
                return "Nouveau mot de passe non fourni", 400
        else:
            return "Utilisateur non trouvé", 404
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return f"Une erreur s'est produite : {str(e)}", 500

# Fonction pour vérifier si un utilisateur existe déjà sur le serveur OwnCloud
def owncloud_user_exists(user_id):
    response = requests.get(OWNCLOUD_API_URL + user_id, auth=tuple(admin_credentials.split(':')))
    return response.status_code

# Fonction pour synchroniser les utilisateurs depuis OwnCloud
def sync_owncloud_users():
    response = requests.get(OWNCLOUD_API_URL.format(userid=""), auth=tuple(admin_credentials.split(':')))
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        user_list = [user.text for user in root.findall(".//data/users/element")]
        for idx, username in enumerate(user_list, start=1):
            existing_user = Users.query.filter_by(username=username).first()
            if existing_user:
                existing_user.username = username
                db.session.merge(existing_user)
            else:
                new_user = Users(username=username, password="default_password")
                db.session.add(new_user)
                db.session.commit()
            print(f"ID: {idx}, Username: {username}")
    else:
        print("Erreur lors de la requête GET")

# Fonction pour vérifier si un utilisateur existe déjà dans la base de données locale.
def user_exists(user_id):
    user = Users.query.filter_by(username=user_id).first()
    print('test user')
    return user is not None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Créer les tables dans la base de données si elles n'existent pas déjà
        sync_owncloud_users()  # Appeler la fonction pour synchroniser les utilisateurs
        all_users = Users.query.all()
        for user in all_users:
            print(f"ID: {user.id}, Username: {user.username}, Password: {user.password}")
    app.run(debug=True, host='0.0.0.0', port=5000)