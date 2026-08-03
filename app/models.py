from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.dialects.postgresql import TSTZRANGE
from sqlalchemy.orm import declarative_base
from sqlalchemy import DateTime
from sqlalchemy.sql import func
Base = declarative_base()

class Resource(Base):
    __tablename__ = "resources"

    r_id = Column(Integer, primary_key=True)
    r_name = Column(String, nullable=False)
    r_cat = Column(String, nullable=True)

class Booking(Base):
    __tablename__ = "bookings"

    b_id = Column(Integer, primary_key=True)
    b_r_id = Column(Integer, ForeignKey("resources.r_id"),nullable=False)
    b_user_id = Column(Integer, nullable=False)
    b_time = Column(TSTZRANGE, nullable=False)
    b_status = Column(String, nullable=False, default="active")
class StatusHistory(Base):
    __tablename__ = "status_history"

    st_id = Column(Integer, primary_key=True)
    st_b_id = Column(Integer, ForeignKey("bookings.b_id"))
    st_status_old = Column(String, nullable=True)
    st_status_new = Column(String, nullable=True)
    st_time = Column(DateTime(timezone=True), server_default=func.now())


class Waitlist(Base):
    __tablename__ = "waitlist"

    w_id = Column(Integer,primary_key=True)
    w_r_id = Column(Integer,ForeignKey("resources.r_id"),nullable=False)
    w_user_id = Column(Integer,nullable=False)
    w_time = Column(TSTZRANGE,nullable=False)