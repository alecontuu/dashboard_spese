# src/config.py
import os
from dotenv import load_dotenv

# Carica variabili d'ambiente da .env (se presente)
load_dotenv()

# ID del Google Sheet (da variabile d'ambiente)
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

if not SHEET_ID:
    raise ValueError("GOOGLE_SHEET_ID non definito. Imposta la variabile d'ambiente.")

# Percorso credenziali (lo cerca nella root del progetto)
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