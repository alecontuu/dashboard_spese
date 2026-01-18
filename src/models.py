# src/models.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class ExpenseRecord(BaseModel):
    """
    Rappresenta una singola spesa validata.
    """
    nome: str = Field(alias="Nome")
    totale: float = Field(alias="Totale")
    data: datetime = Field(alias="Data")
    tipo: str = Field(alias="Tipo")
    paese: str = Field(alias="Paese")
    note: str = Field(default="", alias="Note")

    @field_validator('totale', mode='before')
    @classmethod
    def parse_currency(cls, v):
        if isinstance(v, (float, int)):
            return float(v)
        if isinstance(v, str):
            cleaned = v.replace('€', '').replace(' ', '').replace(',', '.')
            if not cleaned:
                return 0.0
            try:
                return float(cleaned)
            except ValueError:
                raise ValueError(f"Valore non numerico: {v}")
        return 0.0

    @field_validator('data', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%d/%m/%Y")
            except ValueError:
                 raise ValueError(f"Data non valida: {v}")
        return v
    
    class Config:
        populate_by_name = True