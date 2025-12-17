# ===========================================================
# Dockerfile – Projet 5 OpenClassRooms : Importation CSV → MongoDB
# Généré le : 2025-11-30
# Python 3.12 (basé sur python:3.12-slim)
# Ce conteneur exécute :
#   - L'import automatique des données médicales
#   - Les tests unitaires via pytest
# Utilisé conjointement avec docker-compose.yml
# Auteur Erzo
# ===========================================================

FROM python:3.12-slim

# Variables d’environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail dans le conteneur
WORKDIR /app

# D'abord requirements.txt pour tirer parti du cache Docker
COPY requirements.txt .

#  Installer les dépendances sans conserver de fichiers inutiles
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

#  Copier le reste du code (libs/, importer.py, etc.)
# 
COPY . .

#  Commande par défaut (modifiable dans docker-compose)
CMD ["python", "importer.py"]