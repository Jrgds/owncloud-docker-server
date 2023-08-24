import requests
import base64
from config import ADMIN_CREDENTIALS, OWNCLOUD_API_URL

def user_exists_in_owncloud(username):
    response = requests.get(f"{OWNCLOUD_API_URL}/{username}", headers={"Authorization": "Basic " + base64.b64encode(ADMIN_CREDENTIALS.encode()).decode()})
    return response.ok
