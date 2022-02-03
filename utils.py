import os
import json
import numpy as np
import re
import pandas as pd
from config import DATA_PATH, PDF_PATH


def read_data():
    if not os.path.isdir(DATA_PATH):
        os.mkdir(DATA_PATH)

    papers_df = pd.read_csv(f'{DATA_PATH}/df.csv')
    papers_df.drop('Unnamed: 0', axis=1, inplace=True)
    return papers_df


def obj_to_file(a_list, file_name):
    with open(os.path.join(DATA_PATH, f'{file_name}.txt'), 'w') as file:
        json.dump(a_list, file, ensure_ascii=False)


def get_pdf_from_txt_name(df):
    txt_names = df['file'].tolist()
    pdf_files = np.array(os.listdir(PDF_PATH))
    txt_idxes = [int(re.findall('\d+', txt)[0]) - 1 for txt in txt_names]
    our_pdf_files = pdf_files[txt_idxes]
    # arxiv.org/abs/name_pdf.pdf
    df['pdf_file'] = our_pdf_files

    return df
