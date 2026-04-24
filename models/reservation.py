from typing import Literal
from datetime import datetime
from pydantic import BaseModel
from beanie import Document


class Reservation(Document):
    start_time: datetime
    end_time: datetime
    room_number: Literal[101, 102, 103]
    name: str
    desc: str

    class Settings:
        name = "reservations"


class ReservationRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    room_number: Literal[101, 102, 103]
    name: str
    desc: str
