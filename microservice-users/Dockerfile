# Utilisez une image de base Python
FROM python:3.8-slim

# Définissez le répertoire de travail
WORKDIR /app

# Copiez le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installez les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste des fichiers dans le répertoire de travail
COPY . .

# Exposez le port
EXPOSE 5000

# Commande à exécuter au démarrage du conteneur
CMD ["python", "app.py"]