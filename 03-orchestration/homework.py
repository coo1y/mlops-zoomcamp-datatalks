#!/usr/bin/env python
# coding: utf-8

from typing import Tuple
import numpy as np
import scipy
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error

import prefect
from prefect import flow, task

import mlflow
import mlflow.sklearn

CATEGORICAL = ['PULocationID', 'DOLocationID']

@task(retries=3, retry_delay_seconds=1)
def read_dataframe(file_path: str) -> pd.DataFrame:
    """Get data from the specified path which is in parquet format"""

    df = pd.read_parquet(file_path)

    return df


@task
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the data according to the logic given in the homework"""

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    # categorical = ['PULocationID', 'DOLocationID']
    df[CATEGORICAL] = df[CATEGORICAL].astype(str)
    
    return df


@task
def prep_data(df: pd.DataFrame) -> Tuple[scipy.sparse._csr.csr_matrix, np.ndarray]:
    """Prepare data for ML model training"""
    dv = DictVectorizer()

    train_dicts = df[CATEGORICAL].to_dict(orient='records')
    X_train = dv.fit_transform(train_dicts)

    # val_dicts = df_val[CATEGORICAL].to_dict(orient='records')
    # X_val = dv.transform(val_dicts)

    target = 'duration'
    y_train = df[target].values
    # y_val = df_val[target].values

    return X_train, y_train


@task(log_prints=True)
def train_model(X_train: scipy.sparse._csr.csr_matrix, y_train: np.ndarray) -> LinearRegression:
    """Train a LinearRegression model with MLFlow"""

    with mlflow.start_run() as run:
        lr = LinearRegression()
        lr.fit(X_train, y_train)

        y_pred = lr.predict(X_train)

        train_rmse = root_mean_squared_error(y_train, y_pred)

        mlflow.log_metric("train_rmse", train_rmse)

        mlflow.sklearn.log_model(lr, "yellow_taxi_model")

    return lr



@flow
def ml_pipeline() -> None:
    """The main ML pipeline for the homework"""

    # MLflow settings
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("nyc-taxi-experiment")

    # Q1), Q2)
    print("Q1) Answer: Prefect")
    print(f"Q2) Answer: {prefect.__version__}") # 3.4.3

    # Q3) load data
    df = read_dataframe(file_path="data/yellow_tripdata_2023-03.parquet")
    print(f"Q3) Answer: {len(df)}") # 3403766

    # Q4) clean data
    df = clean_dataframe(df=df)
    print(f"Q4) Answer: {len(df)}") # 3316216

    # Q5) train a model
    X_train, y_train = prep_data(df=df)
    lr = train_model(X_train=X_train, y_train=y_train)
    print(f"Q5) Answer: {lr.intercept_}") # 24.778964270944773

    # Q6) observe MLFlow server
    print("Q6) Answer: ...") # 4500


if __name__ == "__main__":
    ml_pipeline()
    