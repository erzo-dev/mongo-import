#!/bin/bash
#Fichier : mongo-init/init_db.sh - wrapper shell pour injecter les credentials  

# Arrêter le script si une commande échoue
set -e

# 1. Vérification des variables critiques pour la sécurité
if [ -z "$MONGO_INITDB_ROOT_USERNAME" ] || [ -z "$WRITER_PWD" ]; then
    echo "ERREUR : Les secrets administrateurs ou applicatifs sont manquants dans l'environnement."
    exit 1
fi

# 2. Création du script d'exécution temporaire
TEMP_SCRIPT=$(mktemp)

# Remplacer tous les placeholders par les variables d'environnement
sed \
    -e "s|__MONGO_HOST__|$MONGO_HOST|g" \
    -e "s|__DB_NAME__|$MONGO_DB_NAME|g" \
    -e "s|__OWNER_USER__|$OWNER_USER|g" \
    -e "s|__OWNER_PWD__|$OWNER_PWD|g" \
    -e "s|__WRITER_USER__|$WRITER_USER|g" \
    -e "s|__WRITER_PWD__|$WRITER_PWD|g" \
    -e "s|__READER_USER__|$READER_USER|g" \
    -e "s|__READER_PWD__|$READER_PWD|g" \
    ./mongo-init/create_users_db.js > "$TEMP_SCRIPT"

echo "Script d'initialisation généré. Connexion à MongoDB..."

# 3. Exécution du script sur MongoDB
# On se connecte en utilisant l'utilisateur root (créé par MONGO_INITDB_ROOT_...)
# pour avoir les droits de créer les nouveaux utilisateurs (app_writer, etc.).
mongosh "mongodb://$MONGO_HOST:$MONGO_PORT/$MONGO_DB_NAME" \
  --username $MONGO_INITDB_ROOT_USERNAME \
  --password $MONGO_INITDB_ROOT_PASSWORD \
  --authenticationDatabase admin \
  --file "$TEMP_SCRIPT"

# 4. Nettoyage
rm "$TEMP_SCRIPT"

echo "Initialisation MongoDB (Utilisateurs et Rôles) terminée avec succès."