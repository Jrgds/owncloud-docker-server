from flask import jsonify
import requests
from modules.owncloud_api import user_exists_in_owncloud
from modules.models import User
from modules.error_handling import handle_sync_error
import base64

def new_func():
    OWNCLOUD_API_URL = "http://localhost:8080/ocs/v1.php/cloud/users"
    return OWNCLOUD_API_URL

OWNCLOUD_API_URL = new_func()
ADMIN_CREDENTIALS = "admin:admin"

def sync_users():
    try:
        users = User.query.all()
        for user in users:
            if not user_exists_in_owncloud(user.username):
                user_data = {
                    "userid": user.username,
                    "password": "password",  # Vous pouvez définir le mot de passe par défaut ici
                    "groups": ["Everyone"]
                }
                headers = {
                    "Authorization": "Basic " + base64.b64encode(ADMIN_CREDENTIALS.encode()).decode()
                }
                response = requests.post(OWNCLOUD_API_URL, data=user_data, headers=headers)
                if not response.ok:
                    return jsonify({"error": f"Échec de la synchronisation de l'utilisateur {user.username}. Code de statut : {response.status_code}"}), 500
        return jsonify({"message": "Synchronisation effectuée avec succès !"}), 200
    except Exception as e:
        return handle_sync_error(f"Une erreur est survenue lors de la synchronisation : {str(e)}"), 500
