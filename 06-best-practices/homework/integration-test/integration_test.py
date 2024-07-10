import pandas as pd
import os

import sys
sys.path.append("..")  # Add parent directory to path

from batch import get_input_path
from tests.test_batch import dt

def main(year:int, month:int):

    input_file = get_input_path(year, month)

    # Create a dataframe:
    input_data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]
    input_columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df_input = pd.DataFrame(input_data, columns=input_columns)

    # save it:
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    if S3_ENDPOINT_URL is not None:
        options = {
            'client_kwargs': {
                'endpoint_url': S3_ENDPOINT_URL
            }
        }

        df_input.to_parquet(
            input_file,
            engine='pyarrow',
            compression=None,
            index=False,
            storage_options=options
        )
    else:
        df_input.to_parquet(
            input_file,
            engine='pyarrow',
            compression=None,
            index=False
        )

if __name__ == "__main__":
    main(2023, 1)