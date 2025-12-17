"""
 Fonction d'import d'un dataset au format CSV vers MongoDB

Exemples d'utilisation :
# Pour lancer des tsts unitaires 
    python importer.py tests

# Analyse le fichier CSV avant import 
    python importer.py analyze

# Verifie la connection à MongoDb
    python importer.py check_mongodb

# Lance l'import 
    python importer.py import

"""

import os
import sys
import pandas as pd
import argparse
import pytest

from pymongo import MongoClient

from services.dataframe_service import analyse_df
from services.mongodb_service import test_crud
from libs.mongoDb.migrate_to_mongodb import migrate_dataframe_to_collection, drop_collection, create_collection
from libs.mongoDb.create_indexes import create_mongodb__indexes
from libs.utils import load_csv, kaggle_download_csv, init_env

init_env()  # Avant de charger les constantes 

from settings.constants import (
    VERSION,
    CSV_PATH,
    DB_NAME,
    COLLECTION_NAME,
    MONGO_PORT_DEFAULT,
    KAGGLE_DATASET_ID,
)

def get_mongo_uri() -> str:

    mongo_user = os.getenv("MONGO_USER")
    mongo_password = os.getenv("MONGO_PASSWORD")
    mongo_host = os.getenv("MONGO_HOST", "host.docker.internal")
    mongo_port = os.getenv("MONGO_PORT", MONGO_PORT_DEFAULT)
    mongo_db = os.getenv("MONGO_DB_NAME", DB_NAME) 

    if not mongo_host or not mongo_port:
        raise ValueError(" MONGO_HOST ou MONGO_PORT est manquant dans les variables d’environnement.")

    if mongo_user and mongo_password:
        # Authentification activée
        mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}"
    else:
        # Mode sans authentification (tests)
        mongo_uri  = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"

    return mongo_uri 

def get_mongo_client(mongodb_uri: str) -> MongoClient | None:
    try:
        client = MongoClient(mongodb_uri)
        print(f"\n >> Test connection à Mongodb {mongodb_uri} ")
        print(client.admin.command("ping"))
        return client 
    except Exception as e:
        print(f"\n>> ECHEC Connexion à MongoDB {mongodb_uri} !")
        print(f" >> EXCEPTION get_mongo_client {e} ")
    return None

def run_crud(mongodb_uri, db_name, collection_name):
    print(" >> Exécution du test CRUD uniquement.")
    client = get_mongo_client(mongodb_uri)
    if client is None:
        sys.exit(1)
    
    db = client[db_name]
    collection = db[collection_name]
    test_crud(collection)

def run_check_mongodb(mongodb_uri):
    client = get_mongo_client(mongodb_uri)
    if client is None:
        sys.exit(1)   

def run_import(df:pd.DataFrame, mongodb_uri, db_name, collection_name):
    # Vérification connection Mongodb
    client = get_mongo_client(mongodb_uri)
    if client is None:
        sys.exit(1)

    db = client[db_name]
    collection = db[collection_name]
    mx_step=4
    step=1

    # 1) Suppression de la coàllection existante
    count = drop_collection(collection)
    if count > 0:
        print(f">> {step}/{mx_step} [OK] Suppression de la collection '{collection_name}' ({count} documents).")
    else:
        print(f">> {step}/{mx_step} [OK] La collection '{collection_name}' est vide.")
    step+=1

    # 2) Creation de la collection 
    if create_collection(db, collection_name) == False:
        print(f"\n[ERREUR] Creation collection {collection_name} ")
        sys.exit(1)
    print(f">> {step}/{mx_step} [OK] Creation collection '{collection_name}' ")
    step+=1
    
    # 3) Ajout des indexes et contraintes .
    if create_mongodb__indexes(collection) == False:
        print("\n [ERROR] create_mongodb__indexes ")
        sys.exit(1)
    print(f">> {step}/{mx_step} [OK] Index correctment ajoutés à la collection '{collection_name}' ")
    step+=1
    
    # 4) Migration des données vers MongoDB
    stats = migrate_dataframe_to_collection(df, collection, batch_size=10_000)
    had_error = stats['had_error']

    if had_error:
        print(f"\n>> {step}/{mx_step} [ERREUR] durant la migration \n")
    else:
        print(f"\n>> {step}/{mx_step} [OK] Migration terminée\n ")
    step+=1

def run_automated_test():
    print(" >> Exécution des tests automatiques (pytest)")
    # soit un fichier précis :
    # result = pytest.main(["-q", "tests/test_normalisers.py"])
    # soit toute la suite de tests :
    result = pytest.main(["-q", "tests"])

    if result != 0:
        print("\n>> [ERREUR] Des tests pytest ont échoué.")
        sys.exit(result)

    print("\n>> [OK] Tous les tests pytest ont réussi.\n")  

def main():
    #Variables d'environement
    mongodb_uri = get_mongo_uri()

    # DB de travail
    db_name = DB_NAME
    collection_name = COLLECTION_NAME

    csv_path = os.getenv("CSV_PATH", CSV_PATH)

    parser = argparse.ArgumentParser(description="Projet Healthcare")
    parser.add_argument(
        "mode",
        nargs="?",          # argument optionnel
        choices=["analyze", "import", "crud", "tests", "check_mongodb"],
        default="import",  # On lance l'import si pas d'argument
        help="Mode à exécuter : analyze, import, crud ou tests"
    )
    args = parser.parse_args()
 
    try:
        print(f"\n* Importer version {VERSION} *")    
        print(f"========================\n") 
        # print(f"  Fichier Csv {csv_path} ")

        if args.mode in ["analyze", "import"]:

            if not os.path.exists(csv_path):          
                # Le dataset n'existe pas, on tente un téléchargement
                kaggle_download_csv(KAGGLE_DATASET_ID, csv_path) 

            # Chargemement du fichier CSV
            df = load_csv(csv_path)
            if df.empty:
                print(f" >>> Le fichier {csv_path} est vide ou absent. Import annulé ")
                sys.exit(1)

            # Vérification & Nettoyage du Dataframe
            df_clean = analyse_df(df)
            if df_clean is None:
                sys.exit(1)

            if args.mode == "import":
                run_import(df_clean, mongodb_uri, db_name, collection_name)
            
        if args.mode == "crud":
            run_crud(mongodb_uri, db_name, collection_name)

        if args.mode == "check_mongodb":
            run_check_mongodb(mongodb_uri)

        if args.mode == "tests":
            run_automated_test()

    except Exception as e:
        print(f"EXCEPTION {e} ")

if __name__ == "__main__":
    main()