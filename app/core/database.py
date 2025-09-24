from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import SQLALCHEMY_DATABASE_URL

def get_db_context():
    try:
        db = LocalSession()
        yield db
    finally:
        db.close()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()