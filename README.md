# Migration des données médicales vers MongoDB 

Ce projet automatise la migration, la normalisation et l'importation de données médicales depuis un dataset Kaggle vers une base de données MongoDB. 
La solution est entièrement conteneurisée pour un déploiement reproductible sur AWS (EC2).


### Source des données
Le projet utilise le Healthcare Dataset de Kaggle: 

https://www.kaggle.com/datasets/prasad22/healthcare-dataset/data?select=healthcare_dataset.csv

Il contient des informations sur les patients, les diagnostics, les traitements, les hospitalisations et la facturation.


### Prérequis : 
* Windows : Docker Desktop avec support WSL2.
* Linux Ubuntu: Docker Engine et Docker Compose installés:
    sudo apt update && sudo apt install -y docker.io docker-compose
    sudo usermod -aG docker $USER
* Un compte AWS pour le deployement sur le cloud.



### 1. Installation & Configuration

### Cloner le projet 
```bash
git clone https://github.com/erzo-dev/mongo-import.git
cd mongo-import
```
### Configuration
Créer un fichier .env à partir du template .env.example 

```bash
cp .env.example ./.env
```

### Configurer les variables d'environements 
    MONGO_DB_NAME, MONGO_HOST, OWNER_USER, etc



## 2. Structure du projet
```text
mongo-import/
├─ docker-compose.yml            # Orchestration des conteneurs (Mongo, setup, app, tests)
├─ Dockerfile.mongo-setup        # Image pour le conteneur d'initialisation Mongo
├─ importer.py                   # Point d'entrée Python (analyse, import, tests, CRUD...)
├─ requirements.txt              # Dépendances Python de l'application
├─ .env.example                  # Modèle de configuration des variables d'environnement
│
├─ data/                         # (Facultatif) Dossier local de données si besoin
├─ data_source/
│    └─ healthcare_dataset.csv   # CSV source (si placé manuellement)
│
├─ libs/                         # Fonctions utilitaires réutilisables
│   ├─ mongodb/
│   │   ├─ validators.py         # Règles de validation JSON Schema pour la collection. Peut être
│   │   │                        # adapté si le format des données évolue.    
│   │   ├─ create_indexes.py     # Création des index MongoDB
│   │   └─ migrate_to_mongodb.py # Logique d'insertion par batch
│   ├─ normalisers.py            # Fonctions de normalisation (âge, dates, etc.)
│   ├─ row_to_json.py            # Transformation d'une ligne CSV en document Mongo
│   └─ utils.py                  # Helpers généraux
│
├─ mongo-init/                      
│   ├─ init_db.sh               # Script shell d'initialisation (utilisateurs, schéma, index)
│   └─ create_users_db.js       # Script MongoDB pour créer les utilisateurs/rôles
│
├─ services/
│   ├─ dataframe_service.py     # Analyse et préparation(nettoyage) du DataFrame
│   └─ mongodb_service.py       # Fonctions CRUD de démonstration sur MongoDB
│
├─ settings/
│   └─ constants.py             # Constantes applicatives.
└─ tests/
    └─ test_normalisers.py      # Tests unitaires sur les fonctions de normalisation
```


## 3. Modèle de données MongoDB

    Chaque ligne du fichier CSV est transformée en document MongoDB
```json
{
    "_id": "<uuid4>",
    "patient": {
        "name": "string",
        "age": "int",
        "gender": "string",
        "blood_type": "string"
    },
    "medical": {
        "condition": "string",
        "test_results": "string"
    },
    "medication": "string",
    "doctor": "string",
    "admission": {
        "hospital": "string",
        "admission_type": "string",
        "room_number": "int",
        "date_of_admission": "ISO Date",
        "discharge_date": "ISO Date"
    },
    "billing": {
        "amount": "float",
        "insurance_provider": "string"
    },
    "createdAt": "ISO Date (UTC)",
    "updatedAt": "ISO Date (UTC)"
}
```

## 4. Déploiement via Docker Compose
```bash
# Nettoyage préalable si nécessaire
docker compose down --remove-orphans -v

# Build et lancement du service MongoDB en mode détaché
docker compose up --build -d mongo

# Initialisation de la DB(Validateurs, Index, Utilisateurs)
docker compose run --rm mongo_setup

# Vérifier la connexion à Mongodb
docker compose run --rm app check_mongodb

```

## 5. Import

### Préparation du Dataset :
* Manuel : Déposez-y le fichier manuellement sous ./data_source
* Automatique : Si absent, il est téléchargé via l'API Kaggle 

```bash
# Lancer les tests unitaires 
docker compose run --rm app tests

# Analyser les données médicales du fichier CSV
docker compose run --rm app analyze

# Lancer l’import
docker compose run --rm app import

# Tester les fonctions CRUD
docker compose run --rm app crud
```

## 6. Deployement sur AWS 

### Préparation de l'instance : 
* Type d'instance : instance t3.small (2 vCPU, 2 Go RAM) sous Ubuntu Server.
* Sécurité        : n'autoriser que votre IP sur le port SSH

### Configuration du serveur :
* Se connecter en SSH
* Lancer les commandes
```bash
sudo apt update 
sudo apt install -y docker.io 
sudo docker-compose version 
sudo usermod -aG docker ubuntu
sudo systemctl status docker
```

### Installation de l'application :
```bash
# Récupérer le projet
git clone https://github.com/erzo-dev/mongo-import.git 

# Aller dans le dossier de travail	
cd  mongo-import

# Copier le fichier d’exemple pour définir les variables d’environnement 
cp .env.example ./.env

# Build et lancement du service MongoDB en mode détaché
sudo docker-compose up build -d mongo

# Initialisation de la DB(Validateurs, Index, Utilisateurs)
sudo docker-compose run --rm mongo_setup

# Vérifier la connexion à Mongodb
sudo docker-compose run --rm app check_mongodb

# Lancer les tests unitaires
sudo docker-compose run --rm app tests
```

### Import :

```bash
# Analyser le fichier csv
sudo docker-compose run --rm app analyze  

# Importer les données
sudo docker-compose run --rm app import
```

Les conteneurs sont lancés avec la commande historique docker-compose (avec un tiret), 
car c’est celle qui est directement disponible sur l’instance EC2 Ubuntu 24.04