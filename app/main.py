
from fastapi import FastAPI
from app.routers import resources,bookings,waitlist

app = FastAPI()

app.include_router(resources.router)
app.include_router(bookings.router)
app.include_router(waitlist.router)