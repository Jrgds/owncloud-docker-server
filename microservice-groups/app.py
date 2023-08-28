from flask import Flask, request
import requests
import base64
from flask_sqlalchemy import SQLAlchemy
import configparser
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(80), unique=True, nullable=False)

OWNCLOUD_API_URL = "http://localhost:8080/ocs/v1.php/cloud/groups"
config = configparser.ConfigParser() # Créer un objet ConfigParser
config.read('config.ini') # Charger les valeurs depuis le fichier config.ini
admin_credentials = config.get('Credentials', 'ADMIN_CREDENTIALS') # Lire la valeur de ADMIN_CREDENTIALS depuis la section Credentials

@app.route('/add_group', methods=['POST'])
def add_group():
    try:
        group_name = request.form.get("group_name")

        if group_exists(group_name) and owncloud_group_exists(group_name):
            return "Le groupe existe déjà."

        group_data = {
            "groupid": group_name,
        }

        headers = {
            "Authorization": "Basic " + base64.b64encode(admin_credentials.encode()).decode()
        }

        response = requests.post(OWNCLOUD_API_URL, data=group_data, headers=headers)

        if response.ok:
            new_group = Groups(groupname=group_name)
            db.session.add(new_group)
            db.session.commit()
            return f"Groupe '{group_name}' ajouté avec succès !"
        else:
            return f"Échec de l'ajout du groupe. Code de statut : {response.status_code}"

    except Exception as e:
        return f"Une erreur s'est produite : {str(e)}"

# Fonction pour vérifier si un group existe déjà sur le serveur OwnCloud
def owncloud_group_exists(groupname):
    response = requests.get(OWNCLOUD_API_URL, auth=tuple(admin_credentials.split(':')))
    return response.status_code

# Fonction pour synchroniser les utilisateurs depuis OwnCloud
def sync_owncloud_groups():
    response = requests.get(OWNCLOUD_API_URL.format(groupname=""), auth=tuple(admin_credentials.split(':')))
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        group_list = [group.text for group in root.findall(".//data/groups/element")]
        for idx, groupname in enumerate(group_list, start=1):
            existing_group = Groups.query.filter_by(groupname=groupname).first()  # Utiliser group_name ici
            if existing_group:
                existing_group.groupname = groupname
                db.session.merge(existing_group)
            else:
                new_user = Groups(groupname=groupname)
                db.session.add(new_user)
                db.session.commit()
            print(f"ID: {idx}, Groupname: {groupname}")
    else:
        print("Erreur lors de la requête GET")

def group_exists(group_name):
    return Groups.query.filter_by(groupname=group_name).first() is not None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Créer les tables dans la base de données si elles n'existent pas déjà
        sync_owncloud_groups()  # Appeler la fonction pour synchroniser
        all_groups = Groups.query.all()
    app.run(debug=True, host='0.0.0.0', port=5000)
