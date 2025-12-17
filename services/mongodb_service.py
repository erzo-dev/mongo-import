"""
services.mongodb_service

"""
import uuid

from datetime import datetime
from pprint import pprint
from datetime import datetime, timezone

def test_crud(collection):
    """
    Testes les commandes de Create / Read / Update / Delete 
    """
    now = datetime.now(timezone.utc)
    id= str(uuid.uuid4())
    
    # Ajout d'un hospitalization 
    new_hospitalization = {
        "_id": id,
        "createdAt": now,
        "updatedAt": now,

        "patient": {
            "name": "Create TestPatient",
            "age": 58,
            "gender": "Male",
            "blood_type": "B+",
        },

        "medical": {
            "condition": "Hypertension",
            "test_results": "Normal",    
        },
        "medication": "Aspirin",
        "doctor": "Test Doctor",        

        "admission": {
            "hospital": "Test Hospital",
            "admission_type": "Routine",
            "room_number": 7, 
            "date_of_admission": datetime(2025, 11, 30),
            "discharge_date": None,  
        },

        "billing": {    
            "amount": 1234.56,
            "insurance_provider": "Test Insurance",
        },
    }

    result = collection.insert_one(new_hospitalization)
    print(f"\n >> Patient inséré Id {result.inserted_id} Name {result}  ")

    # Recherche hospitalization , par non mom patient 
    hospitalization = collection.find_one({"patient.name": "Connor Hansen"})
    print("\n>> Résultat recherche hospitalization' Connor Hansen' ")
    pprint(hospitalization)
   
    hospitalization = collection.find_one({"patient.name": "Create TestPatient"})
    print("\n>> Résultat recherche patient 'Create TestPatient' ") 
   
    pprint(hospitalization)

    # Mise à jour Patient 
    result_update = collection.update_one(
        {"patient.name": "Create TestPatient"},
        {
            "$set": {
                "billing.amount": 15000,
                "medical.test_results": "Improved"
            }
        }
    )
    print(f"\n>> Mise à jour patient : {result_update}  ")

    # Suppression d'un seul record
    result_delete = collection.delete_one({"patient.name": "Create TestPatient"})
    print("\n>> Hospitalization supprimée :", result_delete.deleted_count)
    
    try:
        # Test ajout même hospitatlisation ID. 
        print(f"\n>> Insére de nouveau l'hospitalisation  ")
        result = collection.insert_one(new_hospitalization)
        print(f">> Insertion réussie: {result} ")
    except Exception as e:
        print(f">> Exception attendue {e} ")

    # Suppression Multiple 
    result = collection.delete_many({"patient.name": "Create TestPatient"})
    print("\n>>  Hospitalization(s) supprimée(s) :", result.deleted_count)
