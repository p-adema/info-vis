#!/usr/bin/env python3

"""
This file can be used to merge two CSV datasets together.

Usage: ./merge_datasets.py FILEPATH1 SURVEY_YEAR FILEPATH2 SURVEY_YEAR OUTPUT_FILEPATH

Args:
    FILEPATH1:   First dataset filepath
    SURVEY_YEAR: Creates a new `survey_year` columns with the given value for the first dataset.
                 Use 0 if you don't want to add the `survey_year` columns because it already exists.

    FILEPATH2:   Second dataset filepath
    SURVEY_YEAR: Creates a new `survey_year` columns with the given value for the first dataset.
                 Use 0 if you don't want to add the `survey_year` columns because it already exists.

    OUTPUT_FILEPATH: The filename of where to write the merged dataset to.
"""

import chardet
import pandas as pd
import sys
import numpy as np
import re
import pandas as pd


def merge_unnamed_columns(df):
    new_df_data = {}
    UNNAMED = 'Unnamed:'

    for row_index in range(len(df)):
        curr_col = None

        cols = df.columns.tolist()
        for col_index, col in enumerate(cols):
            value = df.loc[row_index, col]

            if not col.startswith(UNNAMED) and col not in new_df_data:
                new_df_data[col] = []

            if col.startswith(UNNAMED):
                if not value is np.nan:
                    if new_df_data[curr_col][-1] == '':
                        new_df_data[curr_col][-1] += str(value)
                    elif str(value) not in new_df_data[curr_col][-1]:
                        new_df_data[curr_col][-1] += ';' + str(value)

            else:
                curr_col = col
                if (col_index < len(cols)-1 and cols[col_index+1].startswith(UNNAMED)):
                    new_df_data[col].append('')
                else:
                    new_df_data[col].append(value)

    return pd.DataFrame(new_df_data)

def get_year_from_filepath(filename: str) -> int:
    return int(re.sub(r'(\d+).*', '\\1', filename))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: ./merge_datasets.py FILEPATH1 SURVEY_YEAR FILEPATH2 SURVEY_YEAR OUTPUT_FILEPATH')
        sys.exit(1)

    filepath1 = sys.argv[1]
    filepath1_survey_year = int(sys.argv[2])
    filepath2 = sys.argv[3]
    filepath2_survey_year = int(sys.argv[4])
    output_filepath = sys.argv[5]

    print(f'Loading {filepath1}')
    file1 = open(filepath1, 'rb')
    result = chardet.detect(file1.read())
    df1 = merge_unnamed_columns(pd.read_csv(filepath1, encoding=result['encoding'], low_memory=False))
    if filepath1_survey_year > 0:
        df1['survey_year'] = filepath1_survey_year

    print(f'Loading {filepath2}')
    file2 = open(filepath2, 'rb')
    result = chardet.detect(file2.read())
    df2 = merge_unnamed_columns(pd.read_csv(filepath2, encoding=result['encoding'], low_memory=False))
    df2['survey_year'] = filepath2_survey_year

    print(f'Merging {filepath1} and {filepath2} into {output_filepath}')
    pd.concat([df1, df2]).to_csv(output_filepath, index=False)

    print('done')
