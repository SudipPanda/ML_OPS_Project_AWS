import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor

from src.utils.config import CONFIG
import logging
from src.utils.s3 import read_parquet, write_parquet
import subprocess

logger = logging.getLogger(__name__)

def _git_commit()->str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
        
    except Exception as e:
        logger.warning(f"Failed to get git commit hash: {e}")
        return "unknown"

def _build_model()->RandomForestRegressor:
    t = CONFIG.training
    return RandomForestRegressor(
        n_estimators=t.n_estimators,
        max_depth=t.max_depth,
        random_state=t.random_state,
        n_jobs=-1
    )

def train_model(train_path:str , test_path:str):
    mlflow.set_tracking_uri(CONFIG.mlflow.tracking_uri)
    mlflow.search_experiments(CONFIG.mlflow.experiment_name)

    target = CONFIG.data.target_column
    train_df = read_parquet(train_path)
    test_df = read_parquet(test_path)

    x_train , y_train = train_df.drop(columns=[target]), train_df[target]
    x_test , y_test = test_df.drop(columns=[target]), test_df[target]

    with mlflow.start_run() as run:
        model = _build_model()
        model.fit(x_train, y_train)

        preds = model.predict(x_test)

        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        mlflow.log_param("model_type" , CONFIG.training.model_type)
        mlflow.log_param("n_estimators" , CONFIG.training.n_estimators)
        mlflow.log_param("max_depth" , CONFIG.training.max_depth)
        mlflow.log_param("min_samples_leaf" , CONFIG.training.min_samples_leaf)

        mlflow.log_metric("rmse" , rmse)
        mlflow.log_metric("mae" , mae)
        mlflow.log_metric("r2" , r2)

        mlflow.set_tag("git_commit" , _git_commit())
        mlflow.sklearn.log_model(model , artifact_path="model")


        return {
            "run_id": run.info.run_id,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }


if __name__ == "__main__":
    pass
