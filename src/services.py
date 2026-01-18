# src/services.py
import pandas as pd
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from typing import List, Optional
import re
import os

# Import dai nostri moduli interni
from src.config import SHEET_ID, SERVICE_ACCOUNT_FILE, ACCOMMODATION_TYPES
from src.models import ExpenseRecord

class DataService:
    def __init__(self):
        self.current_year = datetime.now().year

    @st.cache_data(ttl=600, show_spinner=False)
    def fetch_and_process_data(_self) -> pd.DataFrame:
        """Recupera dati, valida e applica logica business."""
        
        # 1. Connessione
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            st.error(f"File credenziali non trovato in: {SERVICE_ACCOUNT_FILE}")
            return pd.DataFrame()

        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
            client = gspread.authorize(creds)
            sh = client.open_by_key(SHEET_ID)
        except Exception as e:
            st.error(f"Errore GSheets: {e}")
            return pd.DataFrame()

        # 2. Fetch Raw Data
        worksheets = sh.worksheets()
        if len(worksheets) < 4:
            return pd.DataFrame()
        
        all_records = []
        for ws in worksheets[1:-2]:
            all_records.extend(ws.get_all_records())

        # 3. Validazione Pydantic
        validated_data = []
        for record in all_records:
            # Skip righe vuote
            if not record.get("Nome") and not record.get("Totale"):
                continue
            # Skip spese in Italia
            if record.get("Paese", "").strip().lower() == "italia":
                continue
            try:
                obj = ExpenseRecord(**record)
                validated_data.append(obj)
            except Exception:
                continue

        if not validated_data:
            return pd.DataFrame()

        # 4. Business Logic (Split Alloggi)
        final_rows = _self._apply_accommodation_logic(validated_data)

        # 5. Export a Pandas
        return pd.DataFrame([row.model_dump() for row in final_rows])

    def _apply_accommodation_logic(self, records: List[ExpenseRecord]) -> List[ExpenseRecord]:
        processed = []
        for record in records:
            if record.tipo in ACCOMMODATION_TYPES:
                splits = self._split_single_accommodation(record)
                if splits:
                    processed.extend(splits)
                else:
                    processed.append(record)
            else:
                processed.append(record)
        return processed

    def _split_single_accommodation(self, record: ExpenseRecord) -> Optional[List[ExpenseRecord]]:
        match = re.search(r'(\d{1,2}/\d{1,2})-(\d{1,2}/\d{1,2})', record.note)
        if not match:
            return None

        start_str, end_str = match.groups()
        try:
            d_start = datetime.strptime(f"{start_str}/{self.current_year}", "%d/%m/%Y")
            d_end = datetime.strptime(f"{end_str}/{self.current_year}", "%d/%m/%Y")

            if d_end < d_start:
                d_end = d_end.replace(year=self.current_year + 1)

            delta_days = (d_end - d_start).days
            if delta_days <= 0: return None

            daily_cost = record.totale / delta_days
            new_records = []
            
            for i in range(delta_days):
                curr = d_start + timedelta(days=i)
                # Creiamo nuovo record
                new_rec = record.model_copy(update={
                    "data": curr,
                    "totale": daily_cost,
                    "note": f"{record.note} (Day {i+1}/{delta_days})"
                })
                new_records.append(new_rec)
            return new_records
        except ValueError:
            return None