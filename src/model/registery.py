import logging
import mlflow
import mlflow.sklearn

from mlflow.tracking import MlflowClient
from src.utils.config import CONFIG

logger = logging.getLogger(__name__)

def _client()->MlflowClient:
    mlflow.set_tracking_uri(CONFIG.mlflow.tracking_uri)
    return MlflowClient(tracking_uri=CONFIG.mlflow.tracking_uri)

def register_model(run_id:str):
    model_uri = f"runs:/{run_id}/model"
    result = mlflow.register_model(model_uri , CONFIG.mlflow.registered_model_name)

    logger.info(
        "Registered %s as varsion %s" , CONFIG.mlflow.registered_model_name , result.version , run_id
    )

    return result.version


def promote_to_production(version:str)->None:
    client = _client()

    client.set_registered_model_alias(
        name = CONFIG.mlflow.registered_model_name ,
        alias = "production" , 
        version = version
    )

    logger.info("Promoted %s v%s to Production", CONFIG.mlflow.registered_model_name, version)


def get_production_model_metrics():
    client = _client()

    try:
        mv = client.get_model_version_by_alias(CONFIG.mlflow.registered_model_name, "production")
    except Exception:
        return None
    
    run = client.get_run(mv.run_id)
    rmse = run.data.metrics.get('rmse')

    if rmse is None:
        return None
    
    return {"rmse": rmse, "run_id": mv.run_id, "version": mv.version}


def load_production_model():
    mlflow.set_tracking_uri(CONFIG.mlflow.tracking_uri)
    model_uri = f"models:/{CONFIG.mlflow.registered_model_name}@production"
    return mlflow.sklearn.load_model(model_uri)



            #      TRAINING
            #         │
            #         ▼
            #   MLflow Run #123
            #         │
            #         ├── metrics
            #         ├── parameters
            #         └── model artifact
            #                │
            #                ▼
            #       register_model()
            #                │
            #                ▼
            #       Registered Model
            #         housing-model
            #                │
            #       ┌────────┼────────┐
            #       ▼        ▼        ▼
            #      V1       V2       V3
            #                         │
            #                         │
            #          promote_to_production("3")
            #                         │
            #                         ▼
            #                   production
            #                         │
            #                         ▼
            #                V3 = Production
            #                         │
            #                         ▼
            #              FastAPI / Serving
            #                         │
            #                         ▼
            #       models:/housing-model@production
            #                         │
            #                         ▼
            #                        V3
            #                         │
            #                         ▼
            #                   model.predict()


#     models:/housing-model@production
#           │
#           ▼
#     MLflow Registry
#           │
#           ▼
#     Production → V3
#           │
#           ▼
#        Run ID
#           │
#           ▼
#    Model artifact location
#           │
#           ▼
#           S3 bucket
#           │
#           ▼
#      Model files
#           │
#           ▼
#  sklearn model object