#!/usr/bin/env python
# coding: utf-8

import os
import pickle
import pandas as pd

def get_input_path(year, month):
    #pylint:disable=line-too-long
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)

def get_output_path(year, month):
    #pylint:disable=line-too-long
    default_output_pattern = 's3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)

def read_data(filename:str):
    # check if S3_ENDPOINT_URL is set, and if it is, use it for reading
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    if S3_ENDPOINT_URL is not None:
        print(f"Reading {filename} from Lockalstack S3 at {S3_ENDPOINT_URL}...")
        options = {
            'client_kwargs': {
                'endpoint_url': S3_ENDPOINT_URL,
            }
        }
        df = pd.read_parquet(filename, storage_options=options)
    #otherwise use the usual way
    else:
        print(f"Reading {filename} from the actual S3 service...")
        df = pd.read_parquet(filename)

    return df

def prepare_data(df: pd.DataFrame, categorical:list):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    # Ensures the final data type is string
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    return df

def save_data(df:pd.DataFrame, filename:str):
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    # check if S3_ENDPOINT_URL is set, and if it is, use it for saving
    if S3_ENDPOINT_URL is not None:
        print(f"Saving the dataframe to Lockalstack S3 at {S3_ENDPOINT_URL} as {filename}...")
        options = {
            'client_kwargs': {
                'endpoint_url': S3_ENDPOINT_URL,
            }
        }
        
        df.to_parquet(
            filename,
            engine='pyarrow',
            compression=None,
            index=False,
            storage_options=options
        )
    # otherwise use the usual way
    else:
        print(f"Saving the dataframe to the actual S3 service as {filename}...")
        df.to_parquet(
            filename,
            engine='pyarrow',
            compression=None,
            index=False,
        )

def main(year:int, month:int):

    # Change directory to the directory of this script, so that the model file is found:
    script_path = os.path.abspath(__file__)
    os.chdir(os.path.dirname(script_path))
    #current_dir = os.getcwd()
    #print(f"The current working directory is: {current_dir}")

    input_file = get_input_path(year, month)
    print(f"Input file: {input_file}")
    output_file = get_output_path(year, month)
    print(f"Output file: {output_file}")
    categorical = ['PULocationID', 'DOLocationID']

    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    df = read_data(input_file)
    df = prepare_data(df, categorical)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print('predicted mean duration:', y_pred.mean())

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    save_data(df_result, output_file)

if __name__ == "__main__":
    main(2023, 1)