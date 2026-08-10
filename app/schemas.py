from pydantic import BaseModel,model_validator
from typing import Optional
from datetime import datetime,timedelta
class ResourceCreate(BaseModel):
    r_name: str
    r_cat: Optional[str]=None        # think about whether this needs `str | None` — same nullable question as models.py, one layer up

class ResourceResponse(BaseModel):
    r_id: int
    r_name: str
    r_cat: Optional[str]=None

    class Config:
        from_attributes = True   # lets this schema read directly from a SQLAlchemy object, not just a dict


class BookingCreate(BaseModel):
    b_r_id: int
    b_user_id : int
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def enforce_hour_grid(self):
        self.start_time = self.start_time.replace(minute=0, second=0, microsecond=0)
        self.end_time = self.start_time + timedelta(hours=1)
        return self


class BookingResponse(BaseModel):
    b_id : int
    b_r_id: int
    b_user_id: int
    start_time: datetime
    end_time: datetime
    b_status: str

    class Config:
        from_attributes = True  # lets this schema read directly from a SQLAlchemy object, not just a dict

class WaitlistCreate(BaseModel):
    w_r_id: int
    w_user_id : int
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def enforce_hour_grid(self):
        self.start_time = self.start_time.replace(minute=0, second=0, microsecond=0)
        self.end_time = self.start_time + timedelta(hours=1)
        return self


class WaitlistResponse(BaseModel):
    w_id : int
    w_r_id: int
    w_user_id: int
    start_time: datetime
    end_time: datetime


    class Config:
        from_attributes = True  # lets this schema read directly from a SQLAlchemy object, not just a dict





class StatusHistoryResponse(BaseModel):
    st_id : int
    st_b_id: int
    st_status_old: str
    st_status_new: str
    st_time: datetime


    class Config:
        from_attributes = True  # lets this schema read directly from a SQLAlchemy object, not just a dict

class BookingConflict(BaseModel):
    start_time: datetime
    end_time: datetime

class AvailabilityResponse(BaseModel):
    available: bool
    conflicting_bookings: list[BookingConflict]