# src/config.py
import os

# ID del Google Sheet
SHEET_ID = "INSERISCI_QUI_L_ID_DEL_TUO_FOGLIO_GOOGLE"

# Percorso credenziali (lo cerca nella root del progetto)
SERVICE_ACCOUNT_FILE = os.path.join(os.getcwd(), "service_account.json")

# Categorie che attivano la logica di split giorni
ACCOMMODATION_TYPES = [
    "Ostello", 
    "Albergo", 
    "Appartamento", 
    "Alloggio - Altro"
]