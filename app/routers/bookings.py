from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.database import get_db
from app.schemas import BookingCreate, BookingResponse,StatusHistoryResponse
from app.models import Booking,StatusHistory

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

@router.delete("/bookings/{b_id}", response_model=BookingResponse)
def cancel_booking(b_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.b_id == b_id).first()

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.b_status == "cancelled":
        return BookingResponse(
            b_id=booking.b_id,
            b_r_id=booking.b_r_id,
            b_user_id=booking.b_user_id,
            start_time=booking.b_time.lower,
            end_time=booking.b_time.upper,
            b_status=booking.b_status
        )

    booking.b_status = "cancelled"
    db.commit()
    db.refresh(booking)

    return BookingResponse(
        b_id=booking.b_id,
        b_r_id=booking.b_r_id,
        b_user_id=booking.b_user_id,
        start_time=booking.b_time.lower,
        end_time=booking.b_time.upper,
        b_status=booking.b_status
    )
# @router.delete("/delete/booking/{B_id}",B_id: int,)
# def delete_booking(B_id: int,db : Session = Depends(get_db)):
#     new_booling_rec = db.query(Booking).filter(Booking.b_id==B_id).all()
#     if new_booling_rec.status != "cancelled" :
#         db.query().filter(Booking.b_id==B_id).update(Booking.b_status = "canccelled")
#
#     else
#         return null

@router.get("/bookings/{b_id}/history",response_model=list[StatusHistoryResponse])
def get_history(b_id:int,db:Session=Depends(get_db)):
    booking = db.query(Booking).filter(Booking.b_id == b_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    history = db.query(StatusHistory).filter(StatusHistory.st_b_id == b_id).order_by(StatusHistory.st_time.desc()).all()

    return history