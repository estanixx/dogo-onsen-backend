from pydantic import BaseModel

class DateRequest(BaseModel):
    date: str

class DateTimeRequest(BaseModel):
    datetime: str

