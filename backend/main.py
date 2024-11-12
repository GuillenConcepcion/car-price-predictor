from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
import json
import logging
from contextlib import contextmanager
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Car Price Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/cars_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC_LISTINGS = "cars-db.public.listings"
KAFKA_TOPIC_PREDICTIONS = "cars.public.predictions"

class Car(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)
    year = Column(Integer)
    price = Column(Float)
    transmission = Column(String)
    mileage = Column(Integer)
    fuelType = Column(String)
    tax = Column(Float)
    mpg = Column(Float)
    engineSize = Column(Float)
    predicted_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CarBase(BaseModel):
    model: str = Field(..., example="Fiesta")
    year: int = Field(..., ge=1900, le=datetime.now().year, example=2019)
    price: float = Field(..., gt=0, example=12000)
    transmission: str = Field(..., example="Manual")
    mileage: int = Field(..., ge=0, example=25000)
    fuelType: str = Field(..., example="Petrol")
    tax: float = Field(..., ge=0, example=145)
    mpg: float = Field(..., ge=0, example=55.4)
    engineSize: float = Field(..., gt=0, example=1.0)

    @validator('transmission')
    def validate_transmission(cls, v):
        allowed = {'Manual', 'Automatic', 'Semi-Auto'}
        if v not in allowed:
            raise ValueError(f'transmission must be one of {allowed}')
        return v

    @validator('fuelType')
    def validate_fuel_type(cls, v):
        allowed = {'Petrol', 'Diesel', 'Hybrid', 'Electric'}
        if v not in allowed:
            raise ValueError(f'fuelType must be one of {allowed}')
        return v

class CarCreate(CarBase):
    pass

class CarResponse(CarBase):
    id: int
    predicted_price: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class KafkaManager:
    _producer = None
    _consumer = None
    _consumer_thread = None
    _running = False

    @classmethod
    def get_producer(cls):
        if cls._producer is None:
            cls._producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
        return cls._producer

    @classmethod
    def start_consumer(cls):
        if cls._consumer_thread is None:
            cls._running = True
            cls._consumer_thread = threading.Thread(target=cls._consume_predictions)
            cls._consumer_thread.daemon = True
            cls._consumer_thread.start()

    @classmethod
    def _consume_predictions(cls):
        consumer = KafkaConsumer(
            KAFKA_TOPIC_PREDICTIONS,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='backend-consumer'
        )

        while cls._running:
            try:
                messages = consumer.poll(timeout_ms=1000)
                for topic_partition, msgs in messages.items():
                    for message in msgs:
                        cls._handle_prediction(message.value)
            except Exception as e:
                logger.error(f"Error consuming messages: {str(e)}")
                time.sleep(5)

        consumer.close()

    @classmethod
    def _handle_prediction(cls, prediction_data):
        try:
            with get_db() as db:
                car_id = prediction_data.get('id')
                predicted_price = prediction_data.get('predicted_price')
                
                if car_id and predicted_price:
                    car = db.query(Car).filter(Car.id == car_id).first()
                    if car:
                        car.predicted_price = predicted_price
                        db.commit()
                        logger.info(f"Updated prediction for car {car_id}: £{predicted_price:,.2f}")
        except Exception as e:
            logger.error(f"Error handling prediction: {str(e)}")

# Routes
@app.get("/cars", response_model=List[CarResponse])
def get_cars():
    with get_db() as db:
        cars = db.query(Car).all()
        return cars

@app.post("/cars", response_model=CarResponse)
def create_car(car: CarCreate):
    with get_db() as db:
        db_car = Car(**car.dict())
        db.add(db_car)
        db.commit()
        db.refresh(db_car)
        
        try:
            producer = KafkaManager.get_producer()
            producer.send(KAFKA_TOPIC_LISTINGS, db_car.__dict__)
            producer.flush()
            logger.info(f"Sent car {db_car.id} to Kafka")
        except Exception as e:
            logger.error(f"Error sending to Kafka: {str(e)}")
        
        return db_car

@app.get("/cars/{car_id}", response_model=CarResponse)
def get_car(car_id: int):
    with get_db() as db:
        car = db.query(Car).filter(Car.id == car_id).first()
        if car is None:
            raise HTTPException(status_code=404, detail="Car not found")
        return car

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if engine.connect() else "disconnected"
    }

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    KafkaManager.start_consumer()
    logger.info("Application started, Kafka consumer running")

@app.on_event("shutdown")
async def shutdown_event():
    KafkaManager._running = False
    if KafkaManager._consumer_thread:
        KafkaManager._consumer_thread.join(timeout=5)
    if KafkaManager._producer:
        KafkaManager._producer.close()
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)