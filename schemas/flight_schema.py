from pydantic import BaseModel
from typing import List

class ParsedQuery(BaseModel):
    origin: str
    destination: str
    date: str

class FlightOption(BaseModel):
    airline: str
    price: str
    duration: str
    stops: str
