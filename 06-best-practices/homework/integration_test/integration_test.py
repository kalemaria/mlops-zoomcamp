# pylint: disable=wrong-import-position

import os
import sys

sys.path.append("..")  # Add parent directory to path

from batch import get_input_path, get_output_path, read_data, save_data
from tests.test_batch import generate_fake_input


def main(year: int, month: int):
    input_file = get_input_path(year, month)
    print(f"Input file: {input_file}")
    output_file = get_output_path(year, month)
    print(f"Output file: {output_file}")

    # Create a dataframe with fake data:
    input_df = generate_fake_input()

    # save it:
    save_data(input_df, input_file)

    # Run the batch.py script for the fake data:
    os.system('python ../batch.py')

    # Read the output data and verify the result is correct:
    df_output = read_data(output_file)
    print(df_output)
    sum_predicted_durations = df_output.predicted_duration.sum()
    print(f'Sum of predicted durations: {sum_predicted_durations}')

    assert round(sum_predicted_durations, 2) == 36.28

    print('all good')


if __name__ == "__main__":
    main(2023, 1)
