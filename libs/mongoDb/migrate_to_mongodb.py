"""
Fichier: libs.mongoDb.migrate_to_mongodb

"""
import pandas as pd
from pymongo import errors
from pymongo.errors import CollectionInvalid
from pymongo import MongoClient

from libs.row_to_json import row_to_document
from libs.mongoDb.schemas import HOSPITALIZATION_VALIDATOR

def setup_sharding(client: MongoClient, db_name, collection_name):
    """
    Exemple minimal :
    - active le sharding sur la base 'medical_db'
    - shard la collection 'hospitalizations' avec la clé { _id: 'hashed' }
    
    À exécuter sur un cluster shardé (via mongos), pas sur un simple mongod.
    optimisée pour la répartition uniforme des écritures.
    """

    admin = client["admin"]
    namespace = f"{db_name}.{collection_name}"

    # Active le sharding sur la base
    admin.command("enableSharding", db_name)

    # Sharde la collection sur _id hashé
    admin.command( "shardCollection", namespace, key={"_id": "hashed"},)


def drop_collection(collection) -> int:
    try:
        count = collection.count_documents({})
        if count > 0:
            collection.drop()    
    except Exception as e:
        print(f"\n [ATTENTION] drop_collection {e} ")
        count =-1
    return count
      

def bulk_insert(collection, batch_docs: list[dict]) -> tuple[int, Exception | None]:
    if not batch_docs:
        return 0, None
    try:
        result = collection.insert_many(batch_docs, ordered=False)
        return len(result.inserted_ids), None
    except Exception as e:
        print(f">>\n [ATTENTION] bulk_insert ")
        raise

def migrate_dataframe_to_collection(df: pd.DataFrame, collection, batch_size: int = 10_000) -> dict:
    """
    Migre un DataFrame vers une collection MongoDB, par batch.
    
    - Vide la collection si elle contient déjà des documents.
    - Construit les documents via row_to_document(row).
    - Insère par paquets de `batch_size`.
    - Retourne un dict de stats (insérés, ignorés, etc.).
    """
    total_rows = len(df)

    batch: list[dict] = []
    total_inserted = 0
    batch_index = 0
    skipped_rows = 0
    had_error = False
    try:     
        for i, (_, row) in enumerate(df.iterrows(), start=1):
            # Construction du document
            try:
                doc = row_to_document(row)
            except Exception as e:
                skipped_rows += 1
                print(f">> [ATTENTION] Ligne {i} ignorée (erreur dans row_to_document) : {e}")
                raise # continue

            batch.append(doc)

            # Batch plein OU dernière ligne du dataframe
            is_batch_full = (i % batch_size == 0)
            is_last_row = (i == total_rows)

            if is_batch_full or is_last_row:
                batch_index += 1
                inserted, err = bulk_insert(collection, batch)

                if err is not None:
                    print(f">> [ERREUR] Échec d'insertion du batch {batch_index} : {err}")
                    had_error = True
                    break

                total_inserted += inserted
                print(f"   >> [INFO] Batch {batch_index}: {inserted} documents insérés")
                batch.clear()

        # Bilan final
        mongo_count = collection.count_documents({})
        if total_rows != mongo_count:
            print(f"\n[ERREUR] Le Total inséré      : {mongo_count} n'est conforme au total attendu {total_rows} ! ")
            had_error = True 
        else:            
            print(f"\n[INFO] Toutes les lignes ({mongo_count}), aprés néttoyage, du fichier CSV, ont été importées correctement.")
        
        if skipped_rows >0:
            print(f"[INFO] Lignes ignorées   : {skipped_rows}")
    
    except Exception as e:
        print(f"\n EXCEPTION migrate_dataframe_to_collection : {type(e).__name__} -> {str(e)[:300]}...")
        had_error = True 

    return {
        "total_rows": total_rows,
        "total_inserted": total_inserted,
        "mongo_count": mongo_count,
        "skipped_rows": skipped_rows,
        "batches": batch_index,
        "had_error": had_error,
    }

def create_collection(db, name: str) -> bool:
    """
    Crée (ou met à jour) la collection `name` avec un schéma de validation
    pour les hospitalisations.
    """
    
    validator = HOSPITALIZATION_VALIDATOR

    try:
        db.create_collection(
            name,
            validator=validator,
            validationLevel="strict",
            validationAction="error",
        )
    except CollectionInvalid as e:
        # Si la collection existe déjà, on met à jour le validator
        db.command({
            "collMod": name,
            "validator": validator,
            "validationLevel": "strict",
            "validationAction": "error",
        })

    return True