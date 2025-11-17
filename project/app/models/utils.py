from pydantic import BaseModel

class DateRequest(BaseModel):
    date: str
