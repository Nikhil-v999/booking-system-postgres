from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ResourceCreate,ResourceResponse,AvailabilityResponse, BookingConflict,AvailabilityQuery
from app.models import Resource,Booking
from datetime import datetime
from sqlalchemy import and_,func




router = APIRouter()

@router.post("/resources",response_model=ResourceResponse)
def create_resource(resource: ResourceCreate,db : Session = Depends(get_db)):
    new_resource = Resource(r_name = resource.r_name,r_cat = resource.r_cat)
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource



@router.get("/resources/{r_id}/availability", response_model=AvailabilityResponse)
def check_availability(r_id: int,query : AvailabilityQuery = Depends(), db: Session = Depends(get_db)):
    requested_range = func.tstzrange(query.start_time, query.end_time)

    conflicts = db.query(Booking).filter(
        Booking.b_r_id == r_id,
        Booking.b_status == "active",
        Booking.b_time.op("&&")(requested_range)
    ).all()

    return AvailabilityResponse(
        available=len(conflicts) == 0,
        conflicting_bookings=[
            BookingConflict(start_time=b.b_time.lower, end_time=b.b_time.upper)
            for b in conflicts
        ]
    )
# @router.get("/ping")
# def ping():
#     return {"status" : "g0g"}