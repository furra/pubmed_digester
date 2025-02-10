import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from models import Base

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if db_url is None:
    print("Missing `DATABASE_URL` environment variable. Please add it to the .env file.")
else:
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
