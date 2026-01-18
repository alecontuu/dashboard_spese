# Travel Itinerary Planner - Documentazione Completa

## Contesto e Origine del Progetto

Questo progetto è nato dal seguente prompt iniziale:

> Crea un tool che permetta di creare un itinerario di viaggio facilmente. L'applicativo dovrà mostrare all'utente una serie di input che può inserire, ad esempio date nelle quale vuole viaggiare (max 30 giorni), paese nel quale vuole viaggiare (max 1 nazione), tipologia di viaggio (menu a tendina con scelta multipla tra varie opzioni come "relax", "luxury", "avventura", "culturale") e dati questi input si avvierà un agente che creerà il piano di viaggio perfetto. L'agente dovrà dare come output finale un file markdown che l'utente potrà consultare. Questo avrà varie sezioni: una prima parte di spiegazione dell'itinerario totale e poi un capitolo per ogni giorno di viaggio, dove viene spiegato cosa si farà quel giorno.

---

## Struttura del Progetto

```
dashboard_spese/
├── main.py                 # Punto di ingresso - Applicazione Streamlit
├── pyproject.toml          # Configurazione progetto e dipendenze (UV)
├── uv.lock                 # Lock file dipendenze
├── .python-version         # Versione Python (3.11)
├── .gitignore              # File ignorati da Git
├── README.md               # README (vuoto)
├── DOCUMENTATION.md        # Questo file
└── src/
    ├── __init__.py         # Package marker
    ├── config.py           # Configurazioni e costanti
    ├── models.py           # Modelli Pydantic per validazione dati
    └── services.py         # Servizi per fetch e processing dati
```

---

## Dipendenze e Stack Tecnologico

| Tecnologia | Versione | Scopo |
|------------|----------|-------|
| **Python** | ≥3.11 | Linguaggio base |
| **UV** | - | Package manager moderno (Rust-based) |
| **Streamlit** | ≥1.53.0 | Framework UI web interattivo |
| **Pandas** | ≥2.3.3 | Manipolazione dati tabulari |
| **Plotly** | ≥6.5.2 | Grafici interattivi |
| **Pydantic** | ≥2.12.5 | Validazione e serializzazione dati |
| **gspread** | ≥6.2.1 | Client Google Sheets API |
| **google-auth** | ≥2.47.0 | Autenticazione Google OAuth2 |

---

## Descrizione Dettagliata dei Componenti

### 1. `main.py` - Applicazione Principale

**Scopo**: Punto di ingresso dell'applicazione Streamlit. Gestisce l'interfaccia utente e la visualizzazione dei dati.

**Funzionalità**:

1. **Configurazione Pagina**
   ```python
   st.set_page_config(page_title="Dashboard Spese", layout="wide")
   ```
   Imposta il titolo della pagina e utilizza il layout "wide" per massimizzare lo spazio.

2. **Caricamento Dati**
   - Istanzia `DataService()` per accedere ai dati
   - Chiama `fetch_and_process_data()` per ottenere un DataFrame Pandas processato
   - I dati vengono cachati per 10 minuti (TTL=600s)

3. **Sidebar con Filtri**
   - Crea una colonna `AnnoMese` nel formato "YYYY-MM" per raggruppamento
   - Dropdown per selezionare il mese da visualizzare
   - Default: ultimo mese disponibile

4. **KPI (Key Performance Indicators)**
   - Mostra 3 metriche in colonne affiancate:
     - **Totale Spese**: Somma di tutte le spese del mese
     - **Giorni con Spese**: Numero di giorni unici con almeno una spesa
     - **Media Giornaliera**: Totale diviso per numero di giorni

5. **Grafico a Barre (Plotly)**
   - Asse X: Data
   - Asse Y: Totale spese
   - Colore: Tipo di spesa (categorizzazione)
   - Linea orizzontale rossa a 30€ come riferimento budget

6. **Tabella Dettagliata**
   - Espandibile tramite `st.expander()`
   - Formattazione italiana: Date come DD/MM/YYYY, valori come € X.XX

---

### 2. `src/config.py` - Configurazione

**Scopo**: Centralizza tutte le costanti e configurazioni dell'applicazione.

**Contenuto**:

```python
# ID del Google Sheet da cui leggere i dati
SHEET_ID = "INSERISCI_QUI_L_ID_DEL_TUO_FOGLIO_GOOGLE"

# Percorso al file di credenziali Google Service Account
SERVICE_ACCOUNT_FILE = os.path.join(os.getcwd(), "service_account.json")

# Tipi di spesa che attivano la logica di split per giorni
ACCOMMODATION_TYPES = [
    "Ostello",
    "Albergo",
    "Appartamento",
    "Alloggio - Altro"
]
```

**Note**:
- `SHEET_ID`: Deve essere sostituito con l'ID reale del tuo Google Sheet
- `SERVICE_ACCOUNT_FILE`: Richiede un file `service_account.json` nella root del progetto
- `ACCOMMODATION_TYPES`: Lista di categorie che vengono splittate su più giorni

---

### 3. `src/models.py` - Modelli Dati

**Scopo**: Definisce la struttura dei dati con validazione robusta usando Pydantic v2.

**Modello Principale**:

```python
class ExpenseRecord(BaseModel):
    nome: str                    # Nome/descrizione della spesa
    totale: float                # Importo in euro
    data: datetime               # Data della spesa
    tipo: str                    # Categoria (es: "Cibo", "Albergo")
    paese: str                   # Paese di riferimento
    note: str = ""               # Note opzionali
```

**Validatori Custom**:

1. **`parse_currency()`** - Converte il campo `totale`
   - Input accettati: `float`, `int`, `str`
   - Gestisce formati italiani: `"€ 25,50"` → `25.5`
   - Rimuove simbolo € e spazi
   - Sostituisce virgola con punto
   - Fallback: `0.0` se parsing fallisce

2. **`parse_date()`** - Converte il campo `data`
   - Input accettati: `datetime`, `str`
   - Formato atteso: `"DD/MM/YYYY"` (formato italiano)
   - Parsing: `"15/01/2025"` → `datetime(2025, 1, 15)`
   - Fallback: ritorna il valore originale se parsing fallisce

**Configurazione**:
```python
model_config = ConfigDict(populate_by_name=True)
```
Permette di usare sia nomi lowercase che Title Case per i campi.

---

### 4. `src/services.py` - Servizi Business Logic

**Scopo**: Gestisce il recupero dati da Google Sheets e applica la logica di business.

**Classe Principale**: `DataService`

```python
class DataService:
    def __init__(self):
        self.current_year = datetime.now().year
```

#### Metodo: `fetch_and_process_data()`

**Decoratore**: `@st.cache_data(ttl=600)` - Cache di 10 minuti

**Flusso di Elaborazione**:

1. **Connessione a Google Sheets**
   ```python
   creds = ServiceAccountCredentials.from_json_keyfile_name(
       SERVICE_ACCOUNT_FILE,
       ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
   )
   client = gspread.authorize(creds)
   sheet = client.open_by_key(SHEET_ID)
   ```

2. **Fetch Raw Data**
   - Itera su tutti i worksheet del foglio
   - **Salta**: primo foglio e ultimi 2 fogli
   - Estrae tutti i record come dizionari

3. **Validazione con Pydantic**
   - Converte ogni record a `ExpenseRecord`
   - Salta righe vuote (controllo su campo `Nome`)
   - Ignora silenziosamente record con errori di validazione

4. **Applicazione Business Logic**
   - Chiama `_apply_accommodation_logic()` per gestire spese alloggio

5. **Conversione a DataFrame**
   - Ritorna `pd.DataFrame` con i dati processati

#### Metodo: `_apply_accommodation_logic(records)`

**Scopo**: Trasforma spese di alloggio multi-giorno in spese giornaliere.

**Logica**:
```
Per ogni record:
  SE tipo in ACCOMMODATION_TYPES:
    Prova a splittare → SE successo: aggiungi record splittati
                      → SE fallisce: aggiungi record originale
  ALTRIMENTI:
    Aggiungi record originale
```

#### Metodo: `_split_single_accommodation(record)`

**Scopo**: Divide una singola spesa alloggio su più giorni.

**Input Atteso** nel campo `note`:
- Formato: `"descrizione DD/MM-DD/MM"` (es: `"Hotel Roma 15/01-18/01"`)

**Logica**:
1. Estrae date con regex: `(\d{1,2}/\d{1,2})-(\d{1,2}/\d{1,2})`
2. Calcola numero di giorni tra le date
3. Divide il costo totale per numero di giorni
4. Crea N record, uno per ogni giorno
5. Aggiorna `note` con `" (Day N/totale)"`

**Esempio**:
```
Input:  {nome: "Hotel Roma", totale: 300, note: "15/01-18/01", ...}
Output: [
  {nome: "Hotel Roma", totale: 100, data: 15/01, note: "15/01-18/01 (Day 1/3)"},
  {nome: "Hotel Roma", totale: 100, data: 16/01, note: "15/01-18/01 (Day 2/3)"},
  {nome: "Hotel Roma", totale: 100, data: 17/01, note: "15/01-18/01 (Day 3/3)"}
]
```

**Gestione Errori**:
- Se credenziali mancanti: mostra errore Streamlit, ritorna DataFrame vuoto
- Se parsing date fallisce: ritorna `None` (record non splittato)

---

## Flusso Completo dell'Applicazione

```
┌─────────────────────────────────────────────────────────────────┐
│                        AVVIO (main.py)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              st.set_page_config() - Setup UI                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DataService().fetch_and_process_data()         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  1. Connetti a Google Sheets (service_account.json)       │  │
│  │  2. Leggi tutti i worksheet (esclusi 1° e ultimi 2)       │  │
│  │  3. Valida con Pydantic (ExpenseRecord)                   │  │
│  │  4. Applica business logic (split alloggi)                │  │
│  │  5. Ritorna pd.DataFrame                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         [CACHED 10 min]                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SIDEBAR - Filtro Mese                        │
│         Crea colonna AnnoMese + Selectbox selezione             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         KPI Section                             │
│    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│    │ Totale Mese  │ │ Giorni Spese │ │ Media/Giorno │          │
│    │    €XXX      │ │     NN       │ │    €XX.XX    │          │
│    └──────────────┘ └──────────────┘ └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GRAFICO PLOTLY                             │
│    Barre raggruppate per data, colorate per tipo                │
│    + Linea budget orizzontale a 30€                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TABELLA ESPANDIBILE                           │
│    Dettaglio spese con formattazione italiana                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integrazione Google Sheets

### Requisiti

1. **Google Cloud Project** con API abilitate:
   - Google Sheets API
   - Google Drive API

2. **Service Account**:
   - Creare un Service Account nel progetto
   - Scaricare le credenziali JSON
   - Salvare come `service_account.json` nella root del progetto

3. **Configurazione Sheet**:
   - Condividere il Google Sheet con l'email del Service Account
   - Copiare l'ID del foglio (dall'URL) in `config.py`

### Struttura del Google Sheet

**Colonne attese**:
| Colonna | Tipo | Formato | Esempio |
|---------|------|---------|---------|
| Nome | Testo | - | "Pranzo ristorante" |
| Totale | Numero/Testo | €XX,XX o XX.XX | "€ 25,50" o 25.5 |
| Data | Testo | DD/MM/YYYY | "15/01/2025" |
| Tipo | Testo | - | "Cibo", "Albergo" |
| Paese | Testo | - | "Italia" |
| Note | Testo | - | "Hotel 15/01-18/01" |

**Organizzazione Fogli**:
- Ogni foglio rappresenta tipicamente un mese/periodo
- Il **primo foglio** viene saltato (presumibilmente per template/istruzioni)
- Gli **ultimi 2 fogli** vengono saltati (presumibilmente per summary/altro)

---

## Come Eseguire

### Prerequisiti

```bash
# Installa UV (se non presente)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clona il progetto
cd dashboard_spese
```

### Setup

1. **Configura credenziali Google**:
   ```bash
   # Copia il file service_account.json nella root
   cp /path/to/your/service_account.json .
   ```

2. **Configura Sheet ID**:
   ```python
   # In src/config.py, sostituisci:
   SHEET_ID = "il-tuo-sheet-id"
   ```

3. **Installa dipendenze**:
   ```bash
   uv sync
   ```

### Esecuzione

```bash
uv run streamlit run main.py
```

L'applicazione sarà disponibile su `http://localhost:8501`

---

## Caratteristiche Chiave

| Feature | Descrizione |
|---------|-------------|
| **Caching** | Dati cachati per 10 minuti per performance |
| **Validazione Robusta** | Pydantic gestisce formati monetari e date italiane |
| **Split Alloggi** | Spese multi-giorno divise automaticamente |
| **UI Interattiva** | Streamlit con filtri, KPI, grafici |
| **Grafici Plotly** | Visualizzazione interattiva con hover e zoom |
| **Integrazione Cloud** | Dati persistiti su Google Sheets |

---

## Note per Sviluppo Futuro

### Possibili Estensioni

1. **Multi-valuta**: Supporto per conversione valute
2. **Export**: Generazione report PDF/Excel
3. **Budget personalizzati**: Configurazione budget per categoria
4. **Notifiche**: Alert quando si supera il budget
5. **Multi-utente**: Supporto per più utenti/viaggi

### Struttura Prompt Esterni

Se si volesse estendere il progetto per generare itinerari con AI (come da prompt originale), si potrebbe aggiungere:

```
prompts/
├── itinerary_overview.txt      # Prompt per overview viaggio
├── daily_plan.txt              # Prompt per piano giornaliero
└── activity_suggestions.txt    # Prompt per suggerimenti attività
```

---

## Troubleshooting

| Problema | Causa | Soluzione |
|----------|-------|-----------|
| "Credenziali mancanti" | File service_account.json non trovato | Posiziona il file nella root |
| "Sheet non trovato" | SHEET_ID errato o permessi mancanti | Verifica ID e condivisione |
| Dati non aggiornati | Cache attiva | Aspetta 10 min o riavvia app |
| Errore parsing date | Formato data errato | Usa formato DD/MM/YYYY |
| Totale non calcolato | Formato valuta non riconosciuto | Usa €XX,XX o numero puro |

---

*Documentazione generata il 18/01/2026*
