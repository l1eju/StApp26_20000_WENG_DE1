"""Project settings: data source, selected columns, paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# --- Source ----------------------------------------------------------------
DATASET_ID = "consommation-electrique-par-secteur-dactivite-epci"
PORTAL_URL = f"https://opendata.enedis.fr/datasets/{DATASET_ID}"
# Explore API of the Enedis portal (the Data Fair API at /data-fair/api/v1/ gives the same data).
API_BASE = "https://opendata.enedis.fr/api/explore/v2.1"
LICENSE = "Licence Ouverte / Open Licence version 2.0"
SOURCE_CITATION = (
    "Enedis Open Data, \"Consommation et thermosensibilité d'électricité à la maille EPCI "
    "(par secteur d'activité)\" (electricity consumption and thermosensitivity by EPCI and sector)"
)
TIMEOUT_S = 600

# --- Analysis settings (used by utils/prep.py) -------------------------------
# The EPCI perimeter changes a lot before 2017 (2,472 EPCI in 2011, about 1,200 from 2017)
# and the sector definitions change in 2018, so the main analysis starts in 2018.
ANALYSIS_START_YEAR = 2018
# Realised winter degree-days never go above about 2,850 in the data, so a value
# above this limit is treated as an error (one normal-temperature value is 6,205).
DJU_MAX = 4000
SECTOR_LABELS = {
    "RESIDENTIEL": "Residential",
    "TERTIAIRE": "Services (tertiary)",
    "INDUSTRIE": "Industry",
    "AGRICULTURE": "Agriculture",
    "PETIT_PROFESSIONNEL": "Small professionals (until 2017)",
    "INCONNU": "Unknown",
}

# --- Map -------------------------------------------------------------------
# Map by DEPARTMENT (easier to read and lighter than a map by EPCI).
# Outlines: IGN Admin Express via github.com/gregoiredavid/france-geojson
# (simplified, mainland France, open licence). Properties: "code", "nom".
GEOJSON_PATH = ROOT / "assets" / "departements.json"
GEOJSON_ID_KEY = "properties.code"
GEOJSON_CREDIT = "Contours : IGN Admin Express (via gregoiredavid/france-geojson), Licence ouverte"

# Text columns (the others are numbers).
# Codes must stay text to keep the leading zeros (for example department "01").
STRING_COLUMNS = [
    "code_epci", "nom_epci", "type_epci",
    "code_departement", "nom_departement",
    "code_region", "nom_region",
    "code_categorie_consommation", "code_grand_secteur", "code_secteur_naf2",
]

# --- Extracts --------------------------------------------------------------
# Two targeted downloads instead of all 502,422 rows x 43 columns:
#  - "residentiel": everything about thermosensitivity (Residential sector only)
#  - "secteurs"   : few columns but all rows, for consumption by sector
EXTRACTS = {
    "residentiel": {
        "where": 'code_categorie_consommation="RES"',
        "select": [
            "annee", "code_epci", "nom_epci", "type_epci",
            "code_departement", "nom_departement", "code_region", "nom_region",
            "nb_sites", "conso_totale_mwh", "conso_moyenne_mwh",
            "nombre_de_mailles_secretisees",
            "part_thermosensible", "thermosensibilite_moyenne_kwh_dju",
            "conso_moyenne_usages_thermosensibles_mwh",
            "conso_moyenne_corrigee_de_l_alea_climatique_usages_thermosensibles_mwh",
            "dju_a_tr", "dju_a_tn",
            "nombre_d_habitants", "taux_de_chauffage_electrique",
            "taux_de_logements_collectifs", "taux_de_residences_principales",
            "residences_principales_avant_1919",
            "residences_principales_de_1919_a_1945",
            "residences_principales_de_1946_a_1970",
            "residences_principales_de_1971_a_1990",
            "residences_principales_de_1991_a_2005",
            "residences_principales_apres_2006",
            "residences_principales_les_plus_recentes",
        ],
    },
    "secteurs": {
        "where": None,
        "select": [
            "annee", "code_epci", "code_departement", "code_region",
            "code_categorie_consommation", "code_grand_secteur", "code_secteur_naf2",
            "nb_sites", "conso_totale_mwh",
        ],
    },
}
