from airflow.sdk import DAG
from datetime import datetime, timedelta
import pandas as pd
import xgboost as xgb

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

import mlflow
from mlflow.tracking import MlflowClient
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

from src.data.ingestion import ingest_data
from src.data.preprocessing import preprocess_data
from src.data.validation import validate_data
from src.features.feature_eng import engineer_features

from src.model.registery import register_model,promote_to_production,get_production_model_metrics,load_production_model
from src.training.evaluate import passes_quality_gate
from src.training.train import train_model

default_args = {
    "owner": "airflow",
    "retries":2,
    "retry_delay": timedelta(minutes=5),
}

def _ingest(**_):
    return ingest_data()

def _validate(**kwargs):
    raw_uri = kwargs['ti'].xcom_pull(task_ids='ingest')
    return validate_data(raw_uri)

def _preprocess(**kwargs):
    raw_uri = kwargs['ti'].xcom_pull(task_ids='validate')
    return preprocess_data(raw_uri)

def _feature_engineer(**kwargs):
    preprocessed_uri = kwargs['ti'].xcom_pull(task_ids='preprocess')
    return engineer_features(preprocessed_uri)

def _train(**kwargs):
    features_uri = kwargs['ti'].xcom_pull(task_ids='feature_engineer')
    train_path = f"{features_uri}/train.parquet"
    test_path = f"{features_uri}/test.parquet"
    return train_model(train_path, test_path)

def _quality_gate(**kwargs):
    run_id = kwargs['ti'].xcom_pull(task_ids='train')
    if passes_quality_gate(run_id):
        return "register_model" 
    return "reject_model"

def _register(**kwargs):
    train_result = kwargs['ti'].xcom_pull(task_ids='train')
    version = register_model(train_result['run_id'])
    return version

def _promote(**kwargs):
    version = kwargs['ti'].xcom_pull(task_ids='register_model')
    promote_to_production(version)

with DAG(
    dag_id="training_pipeline",
    description="A DAG for the training pipeline",
    default_args=default_args,
    schedule="@weekly",
    start_date = datetime(2026 , 2, 9),
    catchup=False,
    tags=["training", "mlops"], ) as dag:

    ingest_data = PythonOperator(
        task_id="ingest_data" , python_callable = _ingest)

    validate_data = PythonOperator(
        task_id="validate_data" , python_callable = _validate)
        
    preprocess_data = PythonOperator(
        task_id="preprocess_data" , python_callable = _preprocess)

    feature_engineer = PythonOperator(
        task_id="feature_engineer" , python_callable = _feature_engineer)

    train_model = PythonOperator(
        task_id="train_model" , python_callable = _train)

    quality_gate = PythonOperator(
        task_id="quality_gate" , python_callable = _quality_gate)

    register_model = PythonOperator(
        task_id="register_model" , python_callable = _register)

    promote_to_production = PythonOperator(
        task_id="promote_to_production" , python_callable = _promote)
    
    reject_model = EmptyOperator(
        task_id="reject_model"
    )
    
    (
        ingest_data
        >> validate_data
        >> preprocess_data
        >> feature_engineer
        >> train_model
        >> quality_gate
    )
    quality_gate >> reject_model
    quality_gate >> register_model >> promote_to_production
