import pandas as pd
import mlflow
import boto3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
import os
import pickle
import logging
from pathlib import Path
from botocore.client import Config
import warnings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

def setup_minio():
    """Setup MinIO connection and ensure bucket exists"""
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='minio',
            aws_secret_access_key='minio123',
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )

        try:
            s3_client.head_bucket(Bucket='mlflow')
            logger.info("MLflow bucket exists")
        except:
            s3_client.create_bucket(Bucket='mlflow')
            logger.info("Created MLflow bucket")

    except Exception as e:
        logger.error(f"Error setting up MinIO: {str(e)}")
        raise

def prepare_data(df):
    """Prepare and preprocess the data"""
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_columns:
        df[col] = df[col].astype('float64')

    X = df.drop('price', axis=1)
    y = df['price']

    label_encoders = {}
    categorical_columns = ['model', 'transmission', 'fuelType']
    for column in categorical_columns:
        label_encoders[column] = LabelEncoder()
        X[column] = label_encoders[column].fit_transform(X[column])

    return X, y, label_encoders

def train_model():
    mlflow.set_tracking_uri("http://localhost:5000")
    
    os.environ['AWS_ACCESS_KEY_ID'] = 'minio'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'minio123'
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000'
    
    setup_minio()
    mlflow.set_experiment("car-price-prediction")

    current_dir = Path(__file__).parent.parent
    data_path = current_dir / 'data' / 'ford.csv'
    
    logger.info(f"Loading data from {data_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found at {data_path}")
        
    df = pd.read_csv(data_path)

    X, y, label_encoders = prepare_data(df)

    encoder_path = Path(__file__).parent / 'label_encoders.pkl'
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoders, f)

    numerical_features = ['year', 'mileage', 'tax', 'mpg', 'engineSize']
    scaler = StandardScaler()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    X_train[numerical_features] = scaler.fit_transform(X_train[numerical_features])
    X_test[numerical_features] = scaler.transform(X_test[numerical_features])

    scaler_path = Path(__file__).parent / 'scaler.pkl'
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)

    with mlflow.start_run():
        params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 2,
            'min_samples_leaf': 1,
            'random_state': 42
        }
        
        logger.info("Training Random Forest model...")
        rf = RandomForestRegressor(**params)
        rf.fit(X_train, y_train)

        y_pred = rf.predict(X_test)
        metrics = {
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }

        logger.info(f"Model metrics: {metrics}")

        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        signature = mlflow.models.signature.infer_signature(X_train, rf.predict(X_train))

        mlflow.sklearn.log_model(
            rf,
            "model",
            registered_model_name="car_price_predictor",
            signature=signature
        )

        mlflow.log_artifact(str(encoder_path))
        mlflow.log_artifact(str(scaler_path))

        logger.info("Model and artifacts logged successfully")

        client = mlflow.tracking.MlflowClient()
        model_version = client.search_model_versions("name='car_price_predictor'")[0]
        
        if model_version.current_stage != "Production":
            client.set_registered_model_alias(
                name="car_price_predictor",
                alias="production",
                version=model_version.version
            )
            logger.info("Model set as production version")

if __name__ == "__main__":
    try:
        train_model()
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise