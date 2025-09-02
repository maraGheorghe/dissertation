from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")

print(DB_URL)

try:
    engine = create_engine(DB_URL)
    SessionLocal = sessionmaker(bind=engine)
except Exception as e:
    print("Error here")
    print(e)