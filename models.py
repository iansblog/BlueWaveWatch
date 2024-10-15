from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class SSRSLocationData(Base):
    __tablename__ = 'location_data'
    __table_args__ = {'extend_existing': True}  # Use this if the table already exists    
    id = Column(Integer, primary_key=True)
    data = Column(String)
    last_updated = Column(DateTime)

class TideTimesData(Base):
    __tablename__ = 'tidetimes_data'
    __table_args__ = {'extend_existing': True}  # Use this if the table already exists
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)  # Add latitude
    longitude = Column(Float, nullable=False)  # Add longitude
    data = Column(String)
    last_updated = Column(DateTime)

class WeatherForecastData(Base):
    __tablename__ = 'weather_forecast_data'
    __table_args__ = {'extend_existing': True}  # Add this line
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    data = Column(String)
    last_updated = Column(DateTime)

class MarineWeatherData(Base):
    __tablename__ = 'marine_weather_data'
    __table_args__ = {'extend_existing': True}  # Allows extension if needed
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    data = Column(String)  # Store the JSON response here
    last_updated = Column(DateTime)


# Create SQLite engine and session
engine = create_engine('sqlite:///location_cache.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
