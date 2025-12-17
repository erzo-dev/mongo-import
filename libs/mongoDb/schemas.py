"""
 libs.mongoDb.schemas
 
 Règles de validation du Schema pour la collection 'hospitalizations'.  

"""

from typing import Dict, Any

HOSPITALIZATION_VALIDATOR: Dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["createdAt", "updatedAt", "patient", "admission"],
        "properties": {
            "createdAt": {"bsonType": "date"},
            "updatedAt": {"bsonType": "date"},

            "patient": {
                "bsonType": "object",
                "required": ["name", "gender", "blood_type"],
                "properties": {
                    "name":       {"bsonType": "string"},
                    "age":        {"bsonType": ["int", "double", "null"]},
                    "gender":     {"bsonType": "string"},
                    "blood_type": {"bsonType": "string"},
                },
            },
            
            # Optionnel : peut être complété plus tard
            "medical": {
                "bsonType": "object",
                "properties": {
                    "condition":    {"bsonType": "string"},
                    "test_results": {"bsonType": "string"},
                    "medication":   {"bsonType": "string"},
                },
            },

            # Optionnel : pas forcément connu à la création du séjour
            "doctor": {"bsonType": "string"},
            
            "admission": {
                "bsonType": "object",
                "required": ["hospital", "date_of_admission"],
                "properties": {
                    "hospital":          {"bsonType": "string"},
                    "admission_type":    {"bsonType": "string"},
                    "room_number":       {"bsonType": "int"},
                    "date_of_admission": {"bsonType": "date"},
                    "discharge_date":    {"bsonType": ["date", "null"]},
                },
            },
            
            # Optionnel : la facturation peut être renseignée plus tard
            "billing": {
                "bsonType": "object",
                "properties": {
                    "amount":            {"bsonType": ["double", "decimal", "int"]},
                    "insurance_provider":{"bsonType": "string"},
                },
            },
        },
    }
}
