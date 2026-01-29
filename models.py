from pydantic import BaseModel

class ParsedQuery(BaseModel):
    origin: str
    destination: str
    date: str

class FlightOption(BaseModel):
    airline: str
    price: str
    duration: str
    stops: str
