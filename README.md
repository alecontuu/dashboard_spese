# Dashboard Spese

Dashboard interattiva per il monitoraggio delle spese di viaggio, con dati provenienti da Google Sheets e visualizzazioni Plotly.

## Funzionalità

- **KPI in tempo reale**: totale spese, numero giorni, media giornaliera
- **Grafico interattivo**: spese raggruppate per data e categoria con linea budget di riferimento
- **Filtro per mese**: selezione rapida dal menu laterale
- **Logica split alloggi**: le spese di alloggio su più giorni vengono automaticamente distribuite
- **Cache dati**: aggiornamento automatico ogni 10 minuti

## Requisiti

- Python 3.11+
- [UV](https://docs.astral.sh/uv/) (package manager) - per sviluppo locale
- Account Google Cloud con API Sheets abilitata

---

## Deploy su Streamlit Cloud (Produzione)

Il modo più semplice per portare l'app in produzione.

### 1. Push su GitHub

Assicurati che il repository sia su GitHub (pubblico o privato).

### 2. Configura Streamlit Cloud

1. Vai su [share.streamlit.io](https://share.streamlit.io)
2. Clicca **"New app"**
3. Seleziona il tuo repository GitHub
4. Imposta:
   - **Branch:** `main`
   - **Main file path:** `main.py`

### 3. Configura i Secrets

In Streamlit Cloud, vai su **Settings → Secrets** e incolla:

```toml
GOOGLE_SHEET_ID = "IL_TUO_GOOGLE_SHEET_ID"

[gcp_service_account]
type = "service_account"
project_id = "il-tuo-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "nome@project-id.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

> Copia i valori dal tuo `service_account.json` locale.

### 4. Deploy

Clicca **"Deploy"**. Ogni push su `main` farà il redeploy automatico (CI/CD integrato).

---

## Sviluppo Locale

### 1. Clona il repository

```bash
git clone <url-repository>
cd dashboard_spese
```

### 2. Installa le dipendenze

```bash
uv sync
```

### 3. Configura le credenziali Google

Per accedere ai dati su Google Sheets, serve un file di credenziali Service Account.

#### Come ottenere `service_account.json`:

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto (o selezionane uno esistente)
3. Cerca e abilita **Google Sheets API**
4. Nel menu laterale vai su **IAM & Admin → Service Accounts**
5. Clicca **Create Service Account**
   - Dai un nome (es. "dashboard-spese")
   - Clicca **Create and Continue**
   - Salta i passaggi opzionali e clicca **Done**
6. Clicca sul service account appena creato
7. Vai nella tab **Keys**
8. Clicca **Add Key → Create new key → JSON**
9. Scarica il file e rinominalo `service_account.json`
10. Spostalo nella **root del progetto** (stessa cartella di `main.py`)

> **Importante**: Non committare mai questo file! È già incluso nel `.gitignore`.

### 4. Configura le variabili d'ambiente

Crea un file `.env` nella root del progetto:

```bash
GOOGLE_SHEET_ID=IL_TUO_GOOGLE_SHEET_ID
```

L'ID si trova nell'URL del foglio:
```
https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
```

### 5. Condividi il Google Sheet

Il service account ha bisogno di accesso al foglio:

1. Apri il file `service_account.json` e copia il valore di `client_email`
2. Apri il tuo Google Sheet
3. Clicca **Condividi**
4. Incolla l'email del service account
5. Imposta permesso **Visualizzatore** (o Lettore)
6. Clicca **Invia**

### 6. Avvia l'app

```bash
uv run streamlit run main.py
```

L'applicazione si aprirà nel browser all'indirizzo `http://localhost:8501`

---

## Struttura del progetto

```
dashboard_spese/
├── main.py                           # Entry point Streamlit
├── pyproject.toml                    # Dipendenze (UV)
├── requirements.txt                  # Dipendenze (Streamlit Cloud)
├── service_account.json              # Credenziali Google (solo locale, ignorato da git)
├── .env                              # Variabili d'ambiente (solo locale, ignorato da git)
├── .streamlit/
│   └── secrets.toml.example          # Template per i secrets
└── src/
    ├── config.py                     # Configurazione (Sheet ID, categorie)
    ├── models.py                     # Modelli Pydantic per validazione dati
    └── services.py                   # Logica di fetch e elaborazione dati
```

## Formato dati Google Sheet

Il foglio deve avere queste colonne:

| Colonna | Formato | Esempio |
|---------|---------|---------|
| nome | Testo | "Pranzo ristorante" |
| totale | Valuta italiana | "€ 25,50" |
| data | DD/MM/YYYY | "15/01/2025" |
| tipo | Categoria | "Ristorante" |
| paese | Testo | "Italia" |
| note | Testo (opzionale) | "15/01-18/01" per alloggi |

### Logica split alloggi

Per le categorie di alloggio (Ostello, Albergo, Appartamento, Alloggio - Altro), se nelle note è presente un range di date nel formato `DD/MM-DD/MM`, il costo viene automaticamente diviso per i giorni del soggiorno.

Esempio: un alloggio da €90 con note "15/01-18/01" diventa 3 spese da €30 (una per ogni notte).

## Troubleshooting

### "Could not find service_account.json"
Assicurati che il file sia nella root del progetto e si chiami esattamente `service_account.json`.

### "Permission denied" sul Google Sheet
Verifica di aver condiviso il foglio con l'email del service account (campo `client_email` nel JSON).

### "API not enabled"
Abilita Google Sheets API nella [Google Cloud Console](https://console.cloud.google.com/apis/library/sheets.googleapis.com).

## Stack tecnologico

- **Streamlit** - UI web interattiva
- **Pandas** - Elaborazione dati
- **Plotly** - Grafici interattivi
- **Pydantic** - Validazione dati
- **gspread** - Client Google Sheets API
- **UV** - Package manager moderno
