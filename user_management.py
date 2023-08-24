from flask import request, jsonify
import requests
from modules.owncloud_api import user_exists_in_owncloud
from modules.error_handling import handle_registration_error
from modules.models import db, User, user_exists  # Ajout de user_exists
import base64
from config import ADMIN_CREDENTIALS, OWNCLOUD_API_URL

def register_user():
    username = request.form.get("username")
    password = request.form.get("password")

    if user_exists(username):
        return handle_registration_error("L'utilisateur existe déjà.", 400)

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
        return jsonify({"message": "Utilisateur enregistré avec succès !"}), 201
    else:
        return handle_registration_error(f"Échec de l'enregistrement de l'utilisateur. Code de statut : {response.status_code}", 500)
