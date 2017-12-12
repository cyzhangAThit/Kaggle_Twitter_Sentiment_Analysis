import pandas as pd
import numpy as np
import itertools
import enchant
import multiprocessing
from multiprocessing import Pool

num_partitions = 20
num_cores = multiprocessing.cpu_count()

dict = {}
corpus = open('tweet_typo_corpus.txt', 'rb')
for word in corpus:
    word = word.decode('utf8')
    word = word.split()
    dict[word[1]] = word[3]
corpus.close()

def remove_repetitions(tweet):
    dict_us = enchant.Dict('en_US')
    tweet=tweet.split()
    for i in range(len(tweet)):
        tweet[i]=''.join(''.join(s)[:2] for _, s in itertools.groupby(tweet[i])).replace('#', '')
        if len(tweet[i])>0:
            if not dict_us.check(tweet[i]):
                tweet[i] = ''.join(''.join(s)[:1] for _, s in itertools.groupby(tweet[i])).replace('#', '')
    tweet = ' '.join(tweet)
    return tweet

def spelling_correction(tweet):
    tweet = tweet.split()
    for i in range(len(tweet)):
        if tweet[i] in dict.keys():
            tweet[i] = dict[tweet[i]]
    tweet = ' '.join(tweet)
    return tweet

def clean(tweet):
    tweet = remove_repetitions(tweet)
    tweet = spelling_correction(tweet)
    return tweet.strip().lower()

def parallelize_dataframe(df, func):
    df_split = np.array_split(df, num_partitions)
    pool = Pool(num_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df

def multiply_columns(data):
    data['tweet'] = data['tweet'].apply(lambda x: clean(x))
    return data

X_train = pd.read_pickle("train_tweets_after_preprocess_cnn.pkl")
X_train = parallelize_dataframe(X_train, multiply_columns)
X_train.to_pickle("train_tweets_after_preprocess_cnn_new.pkl")
print("train preprocessing finished!")
