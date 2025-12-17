"""
libs.row_to_json

Rempli le Json à partir d'un ligne du data_set

"""
import pandas as pd
import uuid
from datetime import datetime, timezone


def row_to_document(row: pd.Series) -> dict:
    """Construit un document MongoDB à partir d'une ligne du CSV."""
    now = datetime.now(timezone.utc)
    return {
        "_id": str(uuid.uuid4()),
        "patient": {
            "name": row["Name"],       
            "age": row["Age"],
            "gender": row["Gender"],
            "blood_type": row["Blood Type"],
        },
        "medical": {
            "condition": row["Medical Condition"],
            "test_results": row["Test Results"],
        },
        "medication": row["Medication"], 
        "doctor": row["Doctor"], 
        "admission": {
            "hospital": row["Hospital"],
            "admission_type": row["Admission Type"],
            "room_number": row["Room Number"],
            "date_of_admission": row["Date of Admission"], 
            "discharge_date": row["Discharge Date"],
        },
        "billing": {
            "amount": row["Billing Amount"],
            "insurance_provider": row["Insurance Provider"],
        },
        "createdAt": now,
        "updatedAt": now,
    }
