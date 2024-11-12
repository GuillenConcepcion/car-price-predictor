import os
import json
import mlflow
import pandas as pd
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any
import time
from pathlib import Path
import boto3
from botocore.client import Config
import warnings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

class CarPricePredictor:
    def __init__(self):
        self.model = None
        self.label_encoders = None
        self.scaler = None
        self.consumer = None
        self.producer = None

    def setup_minio(self):
        """Configure MinIO credentials"""
        os.environ['AWS_ACCESS_KEY_ID'] = 'minio'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'minio123'
        os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000'
        
        boto3.client(
            's3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='minio',
            aws_secret_access_key='minio123',
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        logger.info("MinIO credentials configured")

    def load_model_and_artifacts(self) -> None:
        """Load the ML model and preprocessing artifacts"""
        try:
            logger.info("Loading model and artifacts...")
            
            self.setup_minio()
            
            current_dir = Path(__file__).parent
            
            encoder_path = current_dir / 'label_encoders.pkl'
            with open(encoder_path, "rb") as f:
                self.label_encoders = pickle.load(f)
            logger.info("Loaded label encoders")
            
            scaler_path = current_dir / 'scaler.pkl'
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
            logger.info("Loaded scaler")
            
            mlflow.set_tracking_uri("http://localhost:5000")
            
            max_retries = 5
            for i in range(max_retries):
                try:
                    runs = mlflow.search_runs(experiment_ids=["1"])
                    if len(runs) > 0:
                        break
                except Exception as e:
                    if i == max_retries - 1:
                        raise
                    logger.warning(f"Failed to connect to MLflow, retrying... ({i+1}/{max_retries})")
                    time.sleep(5)
            
            if len(runs) == 0:
                raise Exception("No runs found in MLflow")
            
            latest_run = runs.sort_values("start_time", ascending=False).iloc[0]
            run_id = latest_run.run_id
            
            logger.info(f"Loading model from run {run_id}")
            self.model = mlflow.pyfunc.load_model(f"runs:/{run_id}/model")
            logger.info("Model loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading model and artifacts: {str(e)}")
            raise

    def setup_kafka(self) -> None:
        """Initialize Kafka consumer and producer"""
        try:
            KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
            
            self.consumer = KafkaConsumer(
                'cars-db.public.listings',
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='car_price_predictor',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=1000
            )
            
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                retries=5
            )
            
            logger.info("Kafka consumer and producer initialized")
            
        except Exception as e:
            logger.error(f"Error setting up Kafka: {str(e)}")
            raise

    def preprocess_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Preprocess the input data"""
        try:
            df = pd.DataFrame([data])
            
            numeric_columns = ['year', 'mileage', 'tax', 'mpg', 'engineSize']
            for col in numeric_columns:
                df[col] = df[col].astype(float)
            
            categorical_columns = ['model', 'transmission', 'fuelType']
            for column in categorical_columns:
                df[column] = self.label_encoders[column].transform(df[column])
            
            df[numeric_columns] = self.scaler.transform(df[numeric_columns])
            
            return df
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise

    def process_message(self, message: Any) -> Optional[Dict[str, Any]]:
        """Process incoming Kafka message and return prediction"""
        try:
            data = message.value if isinstance(message.value, dict) else json.loads(message.value)
            
            if 'payload' in data and 'after' in data['payload']:
                car_data = data['payload']['after']
            else:
                car_data = data
            
            required_fields = ['model', 'year', 'transmission', 'mileage', 
                             'fuelType', 'tax', 'mpg', 'engineSize']
            
            for field in required_fields:
                if field not in car_data:
                    logger.warning(f"Missing required field: {field}")
                    return None
            
            processed_data = self.preprocess_data(car_data)
            
            prediction = self.model.predict(processed_data)[0]
            
            car_data['predicted_price'] = float(prediction)
            car_data['prediction_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            return car_data
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None

    def run(self) -> None:
        """Main processing loop"""
        logger.info("Starting to consume messages...")
        
        while True:
            try:
                messages = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, msgs in messages.items():
                    for message in msgs:
                        result = self.process_message(message)
                        
                        if result:
                            self.producer.send('cars.public.predictions', value=result)
                            self.producer.flush()
                            
                            logger.info(
                                f"Processed car: {result.get('model', 'Unknown')} "
                                f"({result.get('year', 'Unknown')}). "
                                f"Predicted price: £{result['predicted_price']:,.2f}"
                            )
                
                time.sleep(0.1)
                    
            except KeyboardInterrupt:
                logger.info("Stopping the service...")
                break
                
            except Exception as e:
                logger.error(f"Error in processing loop: {str(e)}")
                time.sleep(5)  
        
        try:
            self.consumer.close()
            self.producer.close()
            logger.info("Kafka connections closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        
        logger.info("Service stopped")

def main():
    """Main entry point"""
    try:
        load_dotenv()
        
        predictor = CarPricePredictor()
        
        predictor.load_model_and_artifacts()
        
        predictor.setup_kafka()
        
        predictor.run()
        
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        raise
    
    finally:
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()