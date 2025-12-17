"""
Module libs.mongoDb.create_indexes

Ajout d'index dans la collection 

"""

def create_mongodb__indexes(collection) -> bool:
    """ Ajout des index pour les recherches dans la collection  """

    try:
        # Recherche par nom
        # 1 = index croissant, -1 = décroissant/
        collection.create_index([("patient.name", 1)] ,name="idx_patient_name")

        # Age du patient
        collection.create_index([("patient.age", 1)], name="idx_patient_age")

        # Condition médicale
        collection.create_index([("medical.condition", 1)] ,name="idx_medical_condition" )

        # Docteur
        collection.create_index([("doctor", 1)], name="idx_doctor")

        # Hôpital + date d'admission
        collection.create_index(
            [("admission.hospital", 1), ("admission.date_of_admission", -1)],
            name="idx_admission_hospital_date"
        )
        return True

    except Exception as e:
        print(f"\n>> EXCEPTION create_indexes {e}")
        return False
    
