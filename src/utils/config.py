import os
from pathlib import Path
from typing import Dict , Any
import yaml
from dataclasses import dataclass, field


_CONFIG_PATH = Path(__file__).resolve().parents[2]/ "config" / "config.yaml"

def _load_raw_config() -> dict[str, Any]:
    with open(_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


@dataclass
class S3Config:
    bucket: str
    raw_prefix: str
    validated_prefix: str
    processed_prefix: str
    features_prefix: str
    models_prefix: str
    logs_prefix: str
    endpoint_url: str
    region: str

    def uri(self, prefix: str, filename: str) -> str:
        return f"s3://{self.bucket}/{prefix}/{filename}"



@dataclass
class MLflowConfig:
    tracking_uri: str
    experiment_name: str
    registered_model_name: str


@dataclass
class TrainingConfig:
    model_type: str
    n_estimators: int
    max_depth: int
    min_samples_leaf: int


@dataclass
class QualityGateConfig:
    max_rmse: float


@dataclass
class DriftConfig:
    psi_threshold: float


@dataclass
class ServingConfig:
    host: str
    port: int
    model_stage: str


@dataclass
class DataConfig:
    source: str
    target_column: str
    test_size: float


@dataclass
class AppConfig:
    project_name: str
    random_seed: int
    data: DataConfig
    s3: S3Config
    mlflow: MLflowConfig
    training: TrainingConfig
    quality_gate: QualityGateConfig
    drift: DriftConfig
    serving: ServingConfig




def load_config() -> AppConfig:
    raw = _load_raw_config()

    s3_raw = raw["s3"]
    # Environment variables win over the YAML defaults. This is the single
    # seam that lets the exact same code run against MinIO locally and S3
    # in AWS -- only S3_ENDPOINT_URL, S3_BUCKET, AWS_REGION change.
    s3 = S3Config(
        bucket=os.environ.get("S3_BUCKET", s3_raw["bucket"]),
        raw_prefix=s3_raw["raw_prefix"],
        validated_prefix=s3_raw["validated_prefix"],
        processed_prefix=s3_raw["processed_prefix"],
        features_prefix=s3_raw["features_prefix"],
        models_prefix=s3_raw["models_prefix"],
        logs_prefix=s3_raw["logs_prefix"],
        endpoint_url=os.environ.get("S3_ENDPOINT_URL", s3_raw.get("endpoint_url", "")),
        region=os.environ.get("AWS_REGION", s3_raw["region"]),
    )

    mlflow_raw = raw["mlflow"]
    mlflow_cfg = MLflowConfig(
        tracking_uri=os.environ.get("MLFLOW_TRACKING_URI", mlflow_raw["tracking_uri"]),
        experiment_name=mlflow_raw["experiment_name"],
        registered_model_name=mlflow_raw["registered_model_name"],
    )

    training_raw = raw["training"]
    training = TrainingConfig(
        model_type=training_raw["model_type"],
        n_estimators=int(training_raw["n_estimators"]),
        max_depth=int(training_raw["max_depth"]),
        min_samples_leaf=int(training_raw["min_samples_leaf"]),
    )

    quality_gate = QualityGateConfig(max_rmse=float(raw["quality_gate"]["max_rmse"]))
    drift = DriftConfig(psi_threshold=float(raw["drift"]["psi_threshold"]))

    serving_raw = raw["serving"]
    serving = ServingConfig(
        host=serving_raw["host"],
        port=int(os.environ.get("SERVING_PORT", serving_raw["port"])),
        model_stage=os.environ.get("MODEL_STAGE", serving_raw["model_stage"]),
    )

    data_raw = raw["data"]
    data = DataConfig(
        source=data_raw["source"],
        target_column=data_raw["target_column"],
        test_size=float(data_raw["test_size"]),
    )

    return AppConfig(
        project_name=raw["project"]["name"],
        random_seed=int(raw["project"]["random_seed"]),
        data=data,
        s3=s3,
        mlflow=mlflow_cfg,
        training=training,
        quality_gate=quality_gate,
        drift=drift,
        serving=serving,
    )


CONFIG = load_config()

