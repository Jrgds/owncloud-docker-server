from flask import Flask
from modules.user_management import register_user
from modules.sync import sync_users
from modules.models import db

app = Flask(__name__)

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

# Routes
app.route('/register', methods=['POST'])(register_user)
app.route('/sync', methods=['POST'])(sync_users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
