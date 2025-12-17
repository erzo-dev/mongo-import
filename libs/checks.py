"""
libs.checks

Fonctions de vérifications du dataframe. 

"""
import pandas as pd

def check_missing_values(df: pd.DataFrame) -> bool:
    """Affiche un résumé lisible des valeurs manquantes."""
    try:
        na_counts = df.isna().sum()
        total_missing = int(na_counts.sum())
        n_lignes, n_colonnes = df.shape
        
        if total_missing == 0:
            print(f">>  [OK] Aucune valeur manquante détectée. {n_lignes} Lignes, {n_colonnes} Colonnes  ")
            return False  # pas d'erreur

        print(f">>  [ATTENTION] {total_missing} valeurs manquantes au total.")
        cols_with_na = na_counts[na_counts > 0].sort_values(ascending=False)

        for col, n in cols_with_na.items():
            pct = (n / len(df) * 100) if len(df) else 0
            print(f" >>  - {col} : {n} lignes manquantes ({pct:.1f} %)")

        return True  # il y a au moins une valeur manquante → erreur potentielle
    except Exception as e:
        print(f"Exception ! {e}")
        return False


def check_column_value_types(df: pd.DataFrame):
    """
    Vérifie que toutes les valeurs de chaque colonne sont du même type,
    en comptant aussi les valeurs nulles (NaN ou None).
    Retourne True s'il y a une erreur de typage.
    Affiche une ligne par colonne, claire et concise.
    """
    erreur_detectee = False
  
    for col in df.columns:
        serie = df[col]
        null_count = serie.isna().sum()

        # Compter les types réels (hors null)
        type_counts = serie.dropna().map(type).value_counts()

        # Construction du résumé des types
        type_summary = ", ".join(f"{t.__name__}: {count}" for t, count in type_counts.items())

        if null_count > 0:
            type_summary += f", null: {null_count}"

        col_formatted = f"{col[:40]: <40}"
        if len(type_counts) == 1:
            print(f"  >> [OK] Colonne: {col_formatted} — {type_summary} ")
        else:
            print(f"  >> [ERREUR] Colonne: {col_formatted} — {type_summary} ")
            erreur_detectee = True

    return erreur_detectee

def check_expected_columns(df, expected_cols):
    """ Vérifie que les colonnes attendues soient présentes """
    current = set(df.columns)
    expected = set(expected_cols)

    missing = expected - current
    extra   = current - expected
    # print("\n>> Colonnes du data set : \n\t", list(df.columns))
    
    if not missing and not extra:
        print("\n>> [OK] Schéma de colonnes conforme.\n")
    else:
        if missing:
            print("\n >> [ATTENTION] Colonnes manquantes :")
            for col in sorted(missing):
                print("  -", col)
        else:
            print("\n>> [OK] Aucune colonne manquante.")

        if extra:
            print("\n>> [INFO] Colonnes supplémentaires détectées:\n")
            for col in sorted(extra):
                print("  -", col)
        else:
            print("\n>> [OK] Aucune colonne supplémentaire.\n")

    return missing, extra

def save_duplicated(df: pd.DataFrame, output_file="doublons_complets_tries.csv"):
    """ Sauvegarde les lignes en doubles pour analyse"""
    # Mask pour toutes les lignes impliquées dans un doublon (original + copies)
    mask_all_dups = df.duplicated(keep=False)

    if mask_all_dups.sum() == 0:
        print(">> Aucun doublon à sauvegarder.")
        return
    
    first_col = df.columns[0]

    print(f">> [INFO] Sauvegarde {output_file} Nombre de lignes impliquées dans au moins un doublon :", mask_all_dups.sum())

    # Extraction + tri + copy 
    df_all_dups = (
        df[mask_all_dups]
        .copy()
        .sort_values(by=first_col)
    )  
    df_all_dups.to_csv(output_file, index=False)
    print(f"\n>> [INFO]  Lignes identiques sauvegardées dans le Fichier '{output_file}' écrit (trié par {first_col}). "
          f"Nombre de lignes : {len(df_all_dups)}")

def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les doublons (lignes identiques sur toutes les colonnes)."""
    before = len(df)
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        print(f"\n>> [ATTENTION] {dup_count} lignes strictement indentiques détectées.")

        save_duplicated(df)
        
        df_no_dup = df.drop_duplicates().reset_index(drop=True)
        after = len(df_no_dup)
        print(f">> [INFO] {before} Lignes avant, {after} Lignes après \n ")
        return df_no_dup
    else:
        print(">> [INFO] Aucune ligne en double détectée.\n")
        return df.copy()

def drop_logical_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les doublons selon certaines colonnes """
    before = len(df)
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        print(f"\n>> [ATTENTION] {dup_count} lignes strictement indentiques détectées.")

        save_duplicated(df)
        
        df_no_dup = df.drop_duplicates().reset_index(drop=True)
        after = len(df_no_dup)
        print(f">> [INFO] {before} Lignes avant, {after} Lignes après \n ")
        return df_no_dup
    else:
        print(">> [INFO] Aucune ligne en double détectée.\n")
        return df.copy()

def show_unique_values(df: pd.DataFrame, cols, max_values= 10):
    """ Recherche et Affiche les valeurs uniques si < 10 """
    print(">> Recherche du nombre de valeurs uniques :")
    for col in cols:
        # Nettoyage : cast en string + strip pour éviter les doublons déguisés
        uniques = df[col].dropna().map(str).map(str.strip)
        valeurs_uniques = sorted(set(uniques))
        nb_uniques = len(valeurs_uniques)
        
        print(f"\n  > '{col}' contient {nb_uniques} valeur(s) unique(s).")
        
        if nb_uniques < max_values:
            print(f"     {', '.join(valeurs_uniques)}")
        else:
            print("  - Trop de valeurs uniques pour affichage.")
        
def find_inconsistent_columns(df: pd.DataFrame):
    """
    Retourne la liste des colonnes incohérentes :
    ce sont les colonnes pour lesquelles, à valeurs identiques
    sur toutes les autres colonnes, on observe plusieurs valeurs possibles.
    """
    cols = df.columns.tolist()
    inconsistent_cols = []

    for col in cols:
        other_cols = [c for c in cols if c != col]

        # Si, pour un même tuple des autres colonnes, col prend > 1 valeur,
        # alors cette colonne est incohérente par rapport aux autres.
        if df.groupby(other_cols)[col].nunique().gt(1).any():
            inconsistent_cols.append(col)

    return inconsistent_cols 

def drop_inconsistent_duplicates(df: pd.DataFrame, inconsistent_cols) -> pd.DataFrame:
    if not inconsistent_cols:
        return df.copy()

    key_cols = [c for c in df.columns if c not in inconsistent_cols]
    df_dedup = df.drop_duplicates(subset=key_cols, keep="first").copy()
    return df_dedup