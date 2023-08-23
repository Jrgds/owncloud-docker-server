from flask import Flask, request
import requests
import base64
from flask_sqlalchemy import SQLAlchemy
import configparser

app = Flask(__name__)

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Group(db.Model):
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

        if group_exists(group_name):
            return "Le groupe existe déjà."

        group_data = {
            "groupid": group_name,
        }

        headers = {
            "Authorization": "Basic " + base64.b64encode(admin_credentials.encode()).decode()
        }

        response = requests.post(OWNCLOUD_API_URL, data=group_data, headers=headers)

        if response.ok:
            new_group = Group(groupname=group_name)
            db.session.add(new_group)
            db.session.commit()
            return f"Groupe '{group_name}' ajouté avec succès !"
        else:
            return f"Échec de l'ajout du groupe. Code de statut : {response.status_code}"

    except Exception as e:
        return f"Une erreur s'est produite : {str(e)}"

def group_exists(group_name):
    return Group.query.filter_by(groupname=group_name).first() is not None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Créer les tables dans la base de données si elles n'existent pas déjà
    app.run(debug=True, host='0.0.0.0', port=5000)
