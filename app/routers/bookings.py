from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.database import get_db
from app.schemas import BookingCreate, BookingResponse
from app.models import Booking

router = APIRouter()
@router.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = Booking(
        b_r_id=booking.b_r_id,
        b_user_id=booking.b_user_id,
        b_time=func.tstzrange(booking.start_time, booking.end_time)
    )
    db.add(new_booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Booking conflicts with an existing active booking")
    db.refresh(new_booking)
    return BookingResponse(
        b_id=new_booking.b_id,
        b_r_id=new_booking.b_r_id,
        b_user_id=new_booking.b_user_id,
        start_time=new_booking.b_time.lower,
        end_time=new_booking.b_time.upper,
        b_status=new_booking.b_status
    )