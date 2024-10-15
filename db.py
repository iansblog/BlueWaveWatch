# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy base model
Base = declarative_base()

# Create an SQLite engine with check_same_thread set to False
engine = create_engine('sqlite:///location_cache.db', echo=False, connect_args={"check_same_thread": False})

# Create a scoped session to handle sessions for each thread
session = scoped_session(sessionmaker(bind=engine))

# Function to initialize the database tables
def init_db():
    Base.metadata.create_all(engine)

# A function to remove the session at the end of the request
def remove_session():
    Session.remove()
