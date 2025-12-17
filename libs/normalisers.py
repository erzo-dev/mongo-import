"""
libs\normalisers.py : fonctions de normalisations
"""

import pandas as pd
from typing import Any

def normalize_name(raw: str | None) -> str | None:
    """'bObBy jACksOn' -> 'Bobby Jackson'."""
    if raw is None:
        return None
    cleaned = raw.strip()
    if not cleaned:
        return None
    return cleaned.title()


def normalize_int(raw) -> int | None:
    """
    Nettoie une valeur censée être un entier.
    - Supprime les espaces
    - Ignore les chaînes vides / NaN
    - Convertit en int si possible
    - Sinon retourne None
    """
    if pd.isna(raw):
        return None
    
    try:
        if isinstance(raw, str):
            raw = raw.strip()
            if raw == "":
                return None
        value = float(raw)
        if value.is_integer():
            return int(value)
        return None
    except (ValueError, TypeError):
        return None


def normalize_float(raw: Any) -> float | None:
    """Normalise une valeur flottante : NaN/None -> None, sinon float(...) ou None si non convertible."""
    if pd.isna(raw):
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None

def normalize_string(raw: Any) -> str | None:
    """
    Normalise une chaîne :
    - NaN/None -> None
    - strip des espaces
    - chaîne vide -> None
    """
    if pd.isna(raw):
        return None
    s = str(raw).strip()
    if not s:
        return None
    return s

def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les colonnes du DataFrame :
    - Dates : conversion en datetime
    - Name : formatage string (strip, title)
    - Age / Room Number : conversion en int
    - Billing Amount : conversion float
    - Autres chaînes : nettoyage
    """
    date_cols = ["Date of Admission", "Discharge Date"]
    int_cols = ["Age", "Room Number"]
    float_cols = ["Billing Amount"]
    string_cols = [
        "Name", "Gender", "Blood Type",
        "Medical Condition",
        "Doctor",  
        "condition",
        "Hospital",
        "Admission Type",
        "Insurance Provider", 
        "Medication",
        "Test Results"    
    ]
    
    # Nom
    if "Name" in df.columns:
        df["Name"] = df["Name"].apply(normalize_name)

    # Dates
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Entiers
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].astype(object).apply(normalize_int)
            #df[col] = pd.Series((normalize_int(v) for v in df[col]),index=df.index,dtype=object,)

    # Flottants
    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_float)

    # Chaînes
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(object).apply(normalize_string)

    return df
