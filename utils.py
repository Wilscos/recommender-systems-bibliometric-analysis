import os
import pandas as pd

DATA_PATH = 'data'
PLOT_PATH = 'plots'


def read_data():    # TODO: Make 'df.csv' customisable
    if not os.path.isdir(DATA_PATH):
        os.mkdir(DATA_PATH)

    papers_df = pd.read_csv(f'{DATA_PATH}/df.csv')
    papers_df.drop('Unnamed: 0', axis=1, inplace=True)
    return papers_df
