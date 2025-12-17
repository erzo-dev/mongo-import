"""
libs.utils

Utilitaires

"""
import os
import sys
import pandas as pd
import requests
import shutil
import kagglehub

from dotenv import load_dotenv
from pathlib import Path

from settings.constants import DOTENV_FILE

def load_csv(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV introuvable : {csv_path}")
    try:
        df = pd.read_csv(csv_path)
        print(f"\n>> Fichier '{csv_path}' chargé avec succès \n -> {len(df)} lignes, {len(df.columns)} Colonnes.")
        return df
    except FileNotFoundError:
        print(f">> Erreur chargement, fichier non trouvé : {csv_path}")
    return None

def download_csv(url: str, csv_path: str) -> Path:
    """
    Télécharge un CSV depuis une URL et le stocke dans csv_path
    Retourne le chemin complet du fichier enregistré.
    """
    try:
        csv_path = Path(csv_path)
        # S'assurer que le dossier existe
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Exception si HTTP != 200
        csv_path.write_bytes(response.content)
        print(f">> [OK] Fichier téléchargé : {csv_path}")
        return csv_path

    except Exception as e:
        print(f">> [ERREUR] Recupération fichier {url} {e} ")
        return None

def kaggle_download_csv(dataset_id: str, csv_path: str) -> Path:
    """
     Télécharge le dataset Kaggle (cache local via kagglehub)
    """
    try:
        csv_path = Path(csv_path)

        # Téléchargement / récupération dans le cache KaggleHub
        dataset_root = Path(kagglehub.dataset_download(dataset_id))
        print(" >> Dataset root:", dataset_root)

        # Fichier source dans le dataset. 
        src_csv = dataset_root / csv_path.name
        if not src_csv.exists():
            raise FileNotFoundError(f"Fichier introuvable dans le dataset : {src_csv}")

        # Copie vers la destination
        shutil.copy2(src_csv, csv_path)
        print(f">> [OK] Copie vers {csv_path}")
        return csv_path
    except Exception as e:
        print(f">> [ERREUR] kaggle_download_csv  {dataset_id} {e} ")
        return None
    
def init_env():
    """Vérifie la présence du fichier .env et le charge."""
    if not os.path.exists(DOTENV_FILE):
        print(f"\n[ERREUR] Fichier {DOTENV_FILE} introuvable.")
        print(f"\n Veuillez copier .env.example vers {DOTENV_FILE} et configurer vos accès.")
        sys.exit(1)
    
    load_dotenv()
   