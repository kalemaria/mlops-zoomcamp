import os
import pickle
import click

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error

import mlflow
mlflow.set_tracking_uri("sqlite:///mlflow.db") # to open mlflow UI, run in the terminal with 'exp-tracking-env' activated: `mlflow ui --backend-store-uri sqlite:///mlflow.db`
mlflow.set_experiment("nyc-taxi-experiment-hw")


def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
def run_train(data_path: str):

    with mlflow.start_run():

        X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
        X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))

        rf = RandomForestRegressor(max_depth=10, random_state=0)
        rf.fit(X_train, y_train)

        min_samples_split = rf.get_params()['min_samples_split']
        mlflow.log_param("min_samples_split", min_samples_split)

        y_pred = rf.predict(X_val)

        rmse = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("rmse", rmse)

if __name__ == '__main__':
    run_train()