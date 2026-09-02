import logging
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.utils.config import CONFIG
from src.utils.s3 import read_parquet, write_parquet
from sklearn.model_selection import train_test_split   
import itertools

logger = logging.getLogger(__name__)

search_space = {
    "n_estimators": [50, 100, 200],
    "max_depth": [None, 10, 20, 30],
}

def tune_hyperparameters(train_path: str):
    mlflow.set_tracking_uri(CONFIG.mlflow.tracking_uri)
    mlflow.search_experiments(CONFIG.mlflow.experiment_name)

    target = CONFIG.data.target_column
    df = read_parquet(train_path)
    X, y = df.drop(columns=[target]), df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=CONFIG.data.test_size, random_state=CONFIG.data.random_state)

    best_score = float("inf")
    best_params : dict = {}

    with mlflow.start_run(run_name="hyperparameter_tuning") as run:
        for values in itertools.product():
             pass