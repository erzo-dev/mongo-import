"""
settings.constants
"""
import os


# Fichier de configuration "
DOTENV_FILE = ".env"

VERSION = 1.00

# Url du dataset 
URL_DATA_SET = "https://www.kaggle.com/datasets/prasad22/healthcare-dataset/data?select=healthcare_dataset.csv"
KAGGLE_DATASET_ID = "prasad22/healthcare-dataset"

# Fichier
CSV_PATH = "./data_source/healthcare_dataset.csv"

# Colonnes attendues du fichier csv
EXPECTED_COLS = [
    "Name",
    "Age",
    "Gender",
    "Blood Type",
    "Medical Condition",
    "Date of Admission",
    "Doctor",
    "Hospital",
    "Insurance Provider",
    "Billing Amount",
    "Room Number",
    "Admission Type",
    "Discharge Date",
    "Medication",
    "Test Results",
]

SHOW_UNIQUES_COLS = [
    'Gender', 
    'Blood Type', 
    'Medical Condition', 
    'Insurance Provider', 
    'Admission Type', 
    'Medication', 
    'Test Results'
]
       
DB_NAME_DEFAULT = "healthcare_db"
COLLECTION_NAME_DEFAULT = "hospitalizations"

DB_NAME = os.getenv("MONGO_DB_NAME", DB_NAME_DEFAULT)
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", COLLECTION_NAME_DEFAULT)

MONGO_PORT_DEFAULT=27017

MONGO_URI = "mongodb://localhost:27017"
MONGO_URI_DOCKER = "mongodb://host.docker.internal:27017"

BATCH_SIZE = 5_000
