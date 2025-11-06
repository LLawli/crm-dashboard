from pydantic import BaseModel
from datetime import datetime

class DateRange(BaseModel):
    start_date: str
    end_date: str

    def validate(self):
        try:
            datetime.strptime(self.start_date, "%Y-%m-%d")
            datetime.strptime(self.end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Dates must be in YYYY-MM-DD format")

    def convert(self):
        return (datetime.strptime(self.start_date, "%Y-%m-%d"), datetime.strptime(self.end_date, "%Y-%m-%d"))

class ConversionQuery(BaseModel):
    group_by: str
    campaigns: list[str] | str
    date_range: DateRange

    def validate(self):
        if self.group_by not in ["utm_source", "utm_medium", "utm_campaign", "utm_term", "created_at"]:
            raise ValueError("group_by must be one of utm_source, utm_medium, utm_campaign, utm_term, created_at")
        if self.group_by == "created_at":
            self.group_by = ("DATE_TRUNC('day', created_at)")
        
class TimeQuery(BaseModel):
    group_by: str
    campaigns: list[str] | str
    date_range: DateRange

    def validate(self):
        if self.group_by not in ["utm_campaign", "utm_source", "utm_term"]:
            raise ValueError("group_by must be one of utm_campaign, utm_source, utm_term")
        
class KPIQuery(BaseModel):
    campaigns: list[str] | str
    date_range: DateRange

    def validate(self):
        self.date_range.validate()

class LeadRequest(BaseModel):
    # UTMs
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    utm_content: str | None = None
    utm_term: str | None = None
    utm_id: str | None = None
    
    # Facebook click id
    fbclid: str | None = None
    gclid: str | None = None
    
    # Código
    code: str | None = None
    
    # Dados pessoais
    name: str | None = None
    whatsapp: str | None = None
    
    # Respostas das perguntas (texto concatenado)
    responses: dict[str, str] | None = None

    class Config:
        extra = "ignore"
