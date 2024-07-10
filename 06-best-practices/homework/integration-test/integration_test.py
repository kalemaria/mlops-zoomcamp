import pandas as pd
import os

import sys
sys.path.append("..")  # Add parent directory to path

from batch import get_input_path, get_output_path, save_data, read_data
from tests.test_batch import dt

def main(year:int, month:int):

    input_file = get_input_path(year, month)
    print(f"Input file: {input_file}")
    output_file = get_output_path(year, month)
    print(f"Output file: {output_file}")

    # Create a dataframe with fake data:
    input_data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]
    input_columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df_input = pd.DataFrame(input_data, columns=input_columns)

    # save it:
    save_data(df_input, input_file)
  
    # Run the batch.py script for the fake data:
    os.system('python ../batch.py')

    # Read the output data and verify the result is correct:
    df_output = read_data(output_file)
    print(df_output)
    sum_predicted_durations = df_output.predicted_duration.sum()
    print(f'Sum of predicted durations: {sum_predicted_durations}')

    assert round(sum_predicted_durations, 2) == 36.28

if __name__ == "__main__":
    main(2023, 1)