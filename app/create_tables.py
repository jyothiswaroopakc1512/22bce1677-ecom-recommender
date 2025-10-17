# app/create_tables.py
from app.db import engine
from app.models import Base

if __name__ == "__main__":
    print("Creating tables in the configured database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
