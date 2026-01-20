# src/config.py
import os
import streamlit as st
from dotenv import load_dotenv

# Carica variabili d'ambiente da .env (se presente, per sviluppo locale)
load_dotenv()


def get_sheet_id() -> str:
    """Recupera SHEET_ID da Streamlit secrets (prod) o env var (dev)."""
    # Prima prova Streamlit secrets (produzione)
    try:
        if "GOOGLE_SHEET_ID" in st.secrets:
            return st.secrets["GOOGLE_SHEET_ID"]
    except FileNotFoundError:
        # secrets.toml non esiste - siamo in sviluppo locale
        pass
    # Fallback a variabile d'ambiente (sviluppo locale)
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID non definito. Imposta la variabile d'ambiente o Streamlit secrets.")
    return sheet_id


# ID del Google Sheet
SHEET_ID = get_sheet_id()

# Percorso credenziali per sviluppo locale
SERVICE_ACCOUNT_FILE = os.path.join(os.getcwd(), "service_account.json")

# Categorie che attivano la logica di split giorni
ACCOMMODATION_TYPES = [
    "Ostello",
    "Albergo",
    "Appartamento",
    "Alloggio - Altro"
]

# Mapping tipi -> macrocategorie
MAPPA_CATEGORIE = {
    # Trasporti
    "Aereo": "Trasporti",
    "Treno": "Trasporti",
    "Bus": "Trasporti",
    "Nave": "Trasporti",
    "Taxi": "Trasporti",
    "Trasporti - Altro": "Trasporti",

    # Cibo
    "Cibo": "Cibo",

    # Alloggio
    "Ostello": "Alloggio",
    "Albergo": "Alloggio",
    "Appartamento": "Alloggio",
    "Alloggio - Altro": "Alloggio",

    # Attività
    "Attività": "Attività",

    # Acquisti
    "Souvenirs": "Acquisti",
    "Abbigliamento": "Acquisti",
    "Tech": "Acquisti",
    "Acquisti - Altro": "Acquisti",

    # Salute
    "Medicine": "Salute",
    "Vaccini": "Salute",
    "Medico/Ospedale": "Salute",
    "Salute - Altro": "Salute",

    # Extra
    "Assicurazione": "Extra",
    "Visto": "Extra",
    "SIM": "Extra",
    "Lavanderia": "Extra",
    "Extra - Altro": "Extra"
}