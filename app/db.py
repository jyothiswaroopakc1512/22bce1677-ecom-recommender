# app/db.py
from sqlalchemy import create_engine
import os
import warnings

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
else:
    warnings.warn("DATABASE_URL not set; falling back to sqlite:///./dev.db for local development")
    engine = create_engine("sqlite:///./dev.db", connect_args={"check_same_thread": False})
