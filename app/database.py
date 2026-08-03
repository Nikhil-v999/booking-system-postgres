import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


POSTGRES_HOST=os.getenv("POSTGRES_HOST")
POSTGRES_PORT=os.getenv("POSTGRES_PORT")
POSTGRES_DB=os.getenv("POSTGRES_DB")
POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
print("HOST:", POSTGRES_HOST, "PORT:", POSTGRES_PORT, "DB:", POSTGRES_DB, "USER:", POSTGRES_USER)


SessionLocal = sessionmaker(bind=engine)
# if __name__ == "__main__":
#     with engine.connect() as conn:
#         print("Connected!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()