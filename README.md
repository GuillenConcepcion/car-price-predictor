# Car Price Predictor

A machine learning system for predicting car prices using MLflow and Streamlit. This project implements a complete pipeline for predicting car prices with an interactive web interface and real-time visualization.

## Architecture

- **Frontend**: Streamlit application for data visualization and interaction
- **Backend**: FastAPI REST API for data management
- **ML Pipeline**: MLflow for model management and serving
- **Storage**: PostgreSQL for data storage, MinIO for model artifacts
  
```mermaid
 graph TB
    UI[Streamlit UI:8501] --> API[FastAPI:8000]
    API --> DB[(PostgreSQL:5432)]
    DB --> DEB[Debezium:8083]
    DEB --> KAFKA[Kafka:9092]
    KAFKA --> ML[ML Service]
    ML --> MLFLOW[MLflow:5000]
    MLFLOW --> MINIO[(MinIO:9000)]
    ML --> KAFKA
    KAFKA --> API
    API --> DB

    ADMIN[Adminer:8081] --> DB
    KAFKAUI[Kafka UI:8080] --> KAFKA
    ZK[Zookeeper:2181] --> KAFKA
    
    subgraph "User Interface"
        UI
        ADMIN
        KAFKAUI
    end

    subgraph "Storage"
        DB
        MINIO
    end

    subgraph "Processing"
        KAFKA
        DEB
        ML
        MLFLOW
        ZK
    end

    style UI fill:#2563eb,stroke:#1d4ed8,color:#fff
    style API fill:#2563eb,stroke:#1d4ed8,color:#fff
    style DB fill:#059669,stroke:#047857,color:#fff
    style MINIO fill:#059669,stroke:#047857,color:#fff
    style KAFKA fill:#4b5563,stroke:#374151,color:#fff
    style ML fill:#7c3aed,stroke:#6d28d9,color:#fff
    style MLFLOW fill:#7c3aed,stroke:#6d28d9,color:#fff

```


## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Stefen-Taime/car-price-predictor
cd car-price-predictor
```

2. Start the services:
```bash
docker-compose up --build
```

3. Train the initial model:
```bash
cd ml_service
python train.py
```

4. Start the FastAPI backend:
```bash
cd backend
uvicorn main:app --reload
```

5. Start the Streamlit frontend:
```bash
cd web-ui
streamlit run app.py
```

6. Access the applications:
- Streamlit UI: http://localhost:8501
- FastAPI Docs: http://localhost:8000/docs
- MLflow UI: http://localhost:5000
- MinIO Console: http://localhost:9001
- Kafka UI: http://localhost:8080

## Project Structure

```
.
├── backend/                # FastAPI backend service
│   ├── main.py            # Main API application
│   └── requirements.txt   # Python dependencies
├── data/                  # Training data
│   └── ford.csv          # Sample car data
├── ml_service/           # ML training and prediction service
│   ├── train.py         # Model training script
│   └── main.py          # Prediction service
├── mlflow/               # MLflow service configuration
├── postgres/            # PostgreSQL initialization scripts
├── web-ui/              # Streamlit frontend application
│   ├── app.py          # Main Streamlit application
│   └── requirements.txt # Python dependencies
├── docker-compose.yml   # Docker services configuration
└── README.md
```

## Features

- Real-time car price predictions
- Interactive data visualization with Streamlit
- RESTful API with FastAPI
- ML model versioning and tracking with MLflow
- Beautiful charts with Plotly
- Scalable architecture
- API documentation with Swagger UI

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd web-ui
pip install -r requirements.txt
streamlit run app.py
```

### ML Service Development

```bash
cd ml_service
pip install -r requirements.txt
python train.py
```

## API Documentation

The API documentation is available at `http://localhost:8000/docs` when the backend service is running. The following endpoints are available:

- `GET /cars`: List all cars
- `POST /cars`: Add a new car
- `GET /cars/{car_id}`: Get car details
- `GET /health`: Check service health

## Data Flow

1. User submits car data through Streamlit interface
2. Data is sent to FastAPI backend
3. ML service makes predictions using MLflow
4. Results are stored in PostgreSQL
5. Updated data is displayed in Streamlit UI

## Technologies Used

- **Backend**:
  - FastAPI for REST API
  - Pydantic for data validation
  - SQLAlchemy for database ORM

- **Frontend**:
  - Streamlit for UI
  - Plotly for data visualization
  - Pandas for data manipulation

- **ML Pipeline**:
  - MLflow for model management
  - scikit-learn for ML models
  - PostgreSQL for data storage
  - MinIO for artifact storage

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## Acknowledgments

- Ford Used Car Dataset
- MLflow for ML model management
- FastAPI for the backend API
- Streamlit for the interactive UI
