#!/usr/bin/env python
# coding: utf-8

import click
import pickle
import pandas as pd
import os

# Constants
categorical = ['PULocationID', 'DOLocationID']

def load_dv_and_model(filename):
    with open(filename, 'rb') as f_in:
        dv, model = pickle.load(f_in)
        return dv, model

def read_data(filename):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df

def transform_data(df, dv):
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    return X_val

def predict(X_val, model):
    y_pred = model.predict(X_val)
    print(f"Standard deviation of the predicted durations: {y_pred.std()}")
    print(f"Mean predicted duration: {y_pred.mean()}")
    return y_pred

def prepare_output(df, year, month, y_pred):
    df['ride_id'] = f'{year}/{month}_' + df.index.astype('str')
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred
    return df_result

def write_result(df_result, filename):
    df_result.to_parquet(
        filename,
        engine='pyarrow',
        compression=None,
        index=False
)
# The size of the output file is 68.6M ~66M

@click.command()
@click.option('--year', required=True, help='Validation year in YYYY format')
@click.option('--month', required=True, help='Validation month in MM format')
def run(year, month):
    # Input / output filenames
    model_file = 'model.bin'
    taxi_type = 'yellow'
    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month}.parquet'
    output_dir = 'output'
    output_file = f'{taxi_type}_tripdata_predictions_{year}-{month}.parquet'

    dv, model = load_dv_and_model(model_file)
    df = read_data(input_file)
    X_val = transform_data(df, dv)
    y_pred = predict(X_val, model)
    df_result = prepare_output(df, year, month, y_pred)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, output_file)
    write_result(df_result, output_path)

if __name__ == '__main__':
    run()