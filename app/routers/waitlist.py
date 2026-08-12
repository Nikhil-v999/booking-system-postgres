from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.schemas import WaitlistResponse, WaitlistCreate
from app.models import Waitlist,Booking

router = APIRouter()

@router.post("/waitlist",response_model=WaitlistResponse)
def waitlist_add(waitlist : WaitlistCreate,db : Session = Depends(get_db)):
    requested_range = func.tstzrange(waitlist.start_time, waitlist.end_time)
    conflicts = db.query(Booking).filter(
        Booking.b_r_id == waitlist.w_r_id,
        Booking.b_status == "active",
        Booking.b_time.op("&&")(requested_range)
    ).all()
    if len(conflicts)==0 :
        raise HTTPException(status_code=400, detail="Slot is available — book it directly instead of waitlisting")

    new_waitlist = Waitlist(
                        w_r_id = waitlist.w_r_id,
                        w_user_id =waitlist.w_user_id,
                        w_time=func.tstzrange(waitlist.start_time, waitlist.end_time)
                    )
    db.add(new_waitlist)
    db.commit()
    db.refresh(new_waitlist)
    return WaitlistResponse(
        w_id=new_waitlist.w_id,
        w_user_id=new_waitlist.w_user_id,
        w_r_id=new_waitlist.w_r_id,
        start_time=new_waitlist.w_time.lower,
        end_time=new_waitlist.w_time.upper
    )
