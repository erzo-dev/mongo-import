"""
tests.test_normalisers

Tests unitaires des fonctions de normalisations

"""

import pandas as pd
import numpy as np
import pytest

from libs.normalisers import (
    normalize_name,
    normalize_int,
    normalize_float,
    normalize_string,
    normalize_dataframe,
)


# ----------------
# Tests unitaires 
# ----------------

@pytest.mark.parametrize("raw, expected", [
    (" bObBy jACksOn ", "Bobby Jackson"),
    ("", None),
    ("   ", None),
    (None, None),
])
def test_normalize_name(raw, expected):
    assert normalize_name(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    (" 42 ", 42),
    ("42.0", 42),
    ("42.8", None),
    ("", None),
    (None, None),
    ("abc", None),
    (np.nan, None),
])
def test_normalize_int(raw, expected):
    assert normalize_int(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("3.14", 3.14),
    (42, 42.0),
    ("", None),
    (None, None),
    ("abc", None),
    (np.nan, None),
])
def test_normalize_float(raw, expected):
    assert normalize_float(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    (" Hello ", "Hello"),
    ("", None),
    ("    ", None),
    (None, None),
    (np.nan, None),
])
def test_normalize_string(raw, expected):
    assert normalize_string(raw) == expected


# ----------------------------
# Test de normalize_dataframe
# ----------------------------
NOT_NULL = object()  # sentinelle pour "doit être non nul"

def assert_series_matches(series: pd.Series, expected: list):
    """
    Compare une Series à une liste de valeurs attendues en gérant:
    - None <-> valeurs manquantes (NaN, NaT, None)
    - NOT_NULL <-> doit être non nul
    - le reste avec un == classique
    """
    actual = series.tolist()
    assert len(actual) == len(expected), "Longueurs différentes"

    for i, (val, exp) in enumerate(zip(actual, expected)):
        if exp is NOT_NULL:
            # on veut juste "pas null"
            assert not pd.isna(val), f"Index {i}: attendu NON NULL, obtenu {val!r}"
        elif exp is None:
            # on accepte NaN / NaT / None
            assert pd.isna(val), f"Index {i}: attendu valeur manquante, obtenu {val!r}"
        else:
            assert val == exp, f"Index {i}: attendu {exp!r}, obtenu {val!r} à l'index {i}"


def test_normalize_dataframe():
    raw_data = {
        "Name": ["  ALice joHNsOn ", None, ""],
        "Age": [" 42", "abc", ""],
        "Billing Amount": ["12345.67", np.nan, "bad"],
        "Gender": [" Male ", "Female", None],
        "Date of Admission": ["2023-01-01", "bad date", None],
        "Room Number": ["101", None, "300"],
        "Test Results": [" Normal ", "Abnormal", None],
    }

    df_raw = pd.DataFrame(raw_data)
    df_clean = normalize_dataframe(df_raw)

    assert_series_matches(df_clean["Name"], ["Alice Johnson", None, None])
    assert_series_matches(df_clean["Age"], [42, None, None])
    assert_series_matches(df_clean["Billing Amount"], [12345.67, None, None])
    assert_series_matches(df_clean["Gender"], ["Male", "Female", None])
    assert_series_matches(df_clean["Date of Admission"], [NOT_NULL, None, None])
    assert_series_matches(df_clean["Room Number"], [101, None, 300])
    assert_series_matches(df_clean["Test Results"], ["Normal", "Abnormal", None])
