import collections
import nltk
import numpy as np
import os
import pandas as pd
import re
from matplotlib import pyplot as plt
from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from tqdm import tqdm
from utils import read_data
from config import PLOT_PATH

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
pd.set_option('display.max_columns', None)
stopwords = nltk.corpus.stopwords.words('english')


def add_word_count(df: pd.DataFrame, col_name: str):
    df['word_count'] = df[col_name].apply(lambda x: len(str(x).split(' ')))

    return df


def pre_processing(df: pd.DataFrame, col_name: str):
    df_len = len(df)

    corpus = []
    for i in tqdm(range(df_len)):
        # Get string from df and remove punctuation
        text = re.sub('[^a-zA-Z]', ' ', df[col_name][i])

        # Remove tags
        text = re.sub('&lt;/?.*?&gt;', ',', text)

        # Remove special characters and digits
        text = re.sub('(\\d|\\W)+', ' ', text)

        # Convert to list from string
        split_text = text.split()

        # Stemming
        # stemmer = PorterStemmer()

        # Lemmatisation
        lemmatizer = WordNetLemmatizer()
        split_lem_text = [lemmatizer.lemmatize(word) for word in split_text if word not in stopwords]
        text = ' '.join(split_lem_text)
        corpus.append(text)

    return corpus


def get_pos_tag(words_list):
    tagged_words = pos_tag(words_list)

    return tagged_words


def corpus_words_frequency(corpus):
    corpus_words = [word for text in corpus for word in text.split(' ')]
    corpus_words_count = collections.Counter(corpus_words)

    return corpus_words_count


def get_words_for_pos(words_list: list, tagged_words: list, pos: str):
    words_to_get = [word for word in tqdm(words_list) if (word, pos) in tagged_words]

    return words_to_get


def bar_plot(words_list: list, frequencies: list, width=0.35, top_k=10):
    x = np.arange(top_k)
    plt.bar(x, frequencies[:top_k], width=width)
    plt.xticks(x, words_list[:top_k], rotation=25)
    plt.title(f'Top {top_k} words by frequency')

    if not os.path.isdir(PLOT_PATH):
        os.mkdir(PLOT_PATH)

    plt.savefig(os.path.join(PLOT_PATH, f'top_{top_k}_words_by_frequency.png'))
    plt.close()


def plot_publications_series(df, remove_years=np.array([])):
    # Creating column 'year'
    df['year'] = df.published.apply(lambda x: x[-4:])

    # Getting data in dictionary
    data = {year: len(df[df.year == year]) for year in df.year.unique()}

    # Remove years if given
    if remove_years:
        for year in remove_years:
            try:
                del data[year]
            except KeyError:
                print(f"The year {year} wasn't in the data! Check again.")
                continue

    # Sorting dictionary by year in ascending order
    sorted_data = sorted(data.items(), key=lambda x: x[0])
    sorted_data = dict(sorted_data)

    # Getting from and to years
    from_year = min(list(sorted_data.keys()))
    to_year = max(list(sorted_data.keys()))

    # Bar plot
    plt.bar(np.arange(len(sorted_data.keys())), list(sorted_data.values()), width=0.35)
    plt.xticks(np.arange(len(sorted_data.keys())), list(sorted_data.keys()))
    plt.title(f'Number of publications from {from_year} to {to_year}')

    if not os.path.isdir(PLOT_PATH):
        os.mkdir(PLOT_PATH)

    plt.savefig(os.path.join(PLOT_PATH, f'bar_plot_publications_per_year_{from_year}-{to_year}.png'))
    plt.close()


def main():
    df = read_data()
    print('Dataframe columns:\n')
    for col in df.columns:
        print(f'- {col}')

    print('\nFirst 5 rows of dataframe: ')
    print(df.head(5))

    # Adding word count column
    df = add_word_count(df, 'summary')
    # Pre-process abstracts
    print('\nPre-processing abstracts ...')
    corpus = pre_processing(df, 'summary')

    # Get words' frequency
    print('\nGetting words\' frequency ...')
    words_count = corpus_words_frequency(corpus)
    words_list = list(words_count.keys())
    # Get tags for unique words
    print('\nGetting words for POS tag ...')
    tagged_words = get_pos_tag(words_list)
    nn_words = get_words_for_pos(words_list, tagged_words, 'NN')
    nns_words = get_words_for_pos(words_list, tagged_words, 'NNS')
    nnp_words = get_words_for_pos(words_list, tagged_words, 'NNP')

    # Concatenating all lists of nouns
    noun_words = nn_words + nns_words + nnp_words

    print('\nGetting words to plot ...')
    words_to_plot = {k: v for k, v in words_count.items() if k in noun_words}
    sorted_words_to_plot = sorted(words_to_plot.items(), key=lambda x: x[1], reverse=True)
    words_to_plot = dict(sorted_words_to_plot)
    # Bar plot of top k words
    bar_plot(list(words_to_plot.keys()), list(words_to_plot.values()))
    # Bar plot of publications per year
    plot_publications_series(df, remove_years=np.array(['2022']))


if __name__ == '__main__':
    main()
