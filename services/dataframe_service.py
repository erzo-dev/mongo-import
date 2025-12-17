"""
services.dataframe_service

Analyse la cohérences des valeurs de chaque colonne du dataframe 

"""

import pandas as pd
from libs.normalisers import normalize_dataframe
from libs.checks import (
    check_expected_columns, 
    check_column_value_types, 
    check_missing_values,
    drop_duplicates,
    show_unique_values,
    find_inconsistent_columns,
    drop_inconsistent_duplicates
)

from settings.constants import EXPECTED_COLS, SHOW_UNIQUES_COLS

def analyse_df(df: pd.DataFrame):
    """ """
    try:
        
        # Normalisation des données 
        df = normalize_dataframe(df)
        print("\n >>[OK] Datafame normalisé ") 
        print(df.head(3))

        # Vérifie que les données ont bien les colonnes attendues
        missing, extra = check_expected_columns(df, EXPECTED_COLS)
        if missing:
            print("\n>> [ERREUR]  Veuillez analyser le fichier ou adpater le code  ")
            return None
        
        # Vérifie que toutes les colonnes aient le même type
        has_errors = check_column_value_types(df)
        if has_errors:
            print("\n>> [ERREUR] Des erreurs de typage ont été détectées dans certaines colonnes.")
            return None
        else:
            print("\n>> [OK] Toutes les colonnes ont des types homogènes.")

        # Vérifie les valeurs manquantes par colonne.
        print("\n>> Vérification de valeurs manquantes par colonne ===")
        result = check_missing_values(df)
        if result == True:
            return None

        # Supprimme les doublons au sens strict
        df_clean = drop_duplicates(df)

        # Recherche de doublons par colonne ayant des valeurs incoherentes
        inconsistent_cols = find_inconsistent_columns(df_clean)
        if inconsistent_cols:
            print(f"\n>> [ATTENTION] Colonne incohérente: {inconsistent_cols}  ")
            # Colonnes "stables" (tout sauf les colonnes incohérentes)
            key_cols = [c for c in df_clean.columns if c not in inconsistent_cols]

            # Lignes qui ont au moins un doublon sur les colonnes stables
            mask_inconsistent_rows = df_clean.duplicated(subset=key_cols, keep=False)

            df_inconsistent_rows = df_clean[mask_inconsistent_rows].sort_values(key_cols)
            print(df_inconsistent_rows.head(6).to_string(index=False))
            #  Dédoublonnage
            df_dedup = drop_inconsistent_duplicates(df_clean, inconsistent_cols)
            print(f"  >> Avant dédoublonnage : {len(df_clean)} lignes")
            print(f"  >> Après dédoublonnage : {len(df_dedup)} lignes")
            df_clean = df_dedup
        else:
            print("\n>> [OK] Aucune colonne incohérente")

        print("\n")
        cols = SHOW_UNIQUES_COLS
        # cols = df.columns
        show_unique_values(df_clean, cols)

        print("\n\n>> [OK] Analyse du dataframe terminée avec succés. \n ")

        return df_clean

    except Exception as e:
        print(f"\n>>[ERREUR] analyse_df {e}  ! ")
    
    return None
