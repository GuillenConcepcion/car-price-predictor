import pytest
import pandas as pd
import numpy as np
from main import CarPricePredictor

@pytest.fixture
def predictor():
    return CarPricePredictor()

def test_preprocess_data(predictor):
    predictor.load_model_and_artifacts()
    
    test_data = {
        "model": "Fiesta",
        "year": 2020,
        "transmission": "Manual",
        "fuelType": "Petrol",
        "mileage": 10000,
        "tax": 150,
        "mpg": 50.0,
        "engineSize": 1.0
    }
    
    result = predictor.preprocess_data(test_data)
    
    assert isinstance(result, pd.DataFrame)
    assert not result.isnull().values.any()