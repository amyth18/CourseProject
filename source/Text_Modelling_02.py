import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from spacy.lang.en.stop_words import STOP_WORDS as stopwords

from sklearn.decomposition import NMF
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

import sys
from mongo_client import MongoDBClient
from logger import logger

Number_of_Topics = None


def display_topics(model, features, no_top_words=3):
    topics_list = []
    for topic, words in enumerate(model.components_):
        total = words.sum()
        largest = words.argsort()[::-1] # invert sort order
        str2 = "Topic %02d" % topic
        str1 = ""
        for i in range(0, no_top_words):
            #str2 = str("  %s (%2.2f)" % (features[largest[i]], abs(words[largest[i]]*100.0/total)))
            str2 = str("  %s " % (features[largest[i]]))
            if i < (no_top_words-1):
                str1 = str1 + str2 + "+"
            else:
                str1 = str1 + str2
        topics_list.append(str1)
    return topics_list

def addToDf(W_text_matrix, all_topics, method_name, df):
    # add topic to dataframe
    i = 0
    df.loc[:, method_name] = ""
    for r in W_text_matrix:
        loc = np.where(r == np.amax(r))[0][0]
        df.iat[i, df.columns.get_loc(method_name)] = all_topics[loc]
        i += 1
    return df

def NMF_process(tfidf_text_vectorizer, tfidf_text_vectors, df):
    nmf_text_model = NMF(n_components=Number_of_Topics, random_state=42)
    W_text_matrix = nmf_text_model.fit_transform(tfidf_text_vectors)
    #H_text_matrix = nmf_text_model.components_

    all_topics = display_topics(nmf_text_model, tfidf_text_vectorizer.get_feature_names())
    df = addToDf(W_text_matrix, all_topics, "NMF_topic", df)
    return df


def TruncuatedSVD_process(tfidf_text_vectorizer, tfidf_text_vectors, df):
    svd_text_model = TruncatedSVD(n_components=Number_of_Topics, random_state=42)
    W_svd_text_matrix = svd_text_model.fit_transform(tfidf_text_vectors)
    #H_svd_text_matrix = svd_text_model.components_

    all_topics = display_topics(svd_text_model, tfidf_text_vectorizer.get_feature_names())
    df = addToDf(W_svd_text_matrix, all_topics, "TruncatedSVD_topic", df)
    return df

def LDA_process(count_text_vectorizer, count_text_vectors, df):
    lda_text_model = LatentDirichletAllocation(n_components=Number_of_Topics, random_state=42)
    W_lda_text_matrix = lda_text_model.fit_transform(count_text_vectors)
    #H_lda_text_matrix = lda_text_model.components_
    all_topics = display_topics(lda_text_model, count_text_vectorizer.get_feature_names())
    df = addToDf(W_lda_text_matrix, all_topics, "LDA_topic", df)
    return df

def do_for_subset(iteration_number, number_of_rows, Num_rows, df_main):

    start_row = iteration_number*Num_rows
    end_row = start_row+number_of_rows
    df = df_main.iloc[start_row:end_row,:]
    tfidf_text_vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words=stopwords, min_df=1, max_df=0.8)
    tfidf_text_vectors = tfidf_text_vectorizer.fit_transform(df['text'])

    df = NMF_process(tfidf_text_vectorizer, tfidf_text_vectors, df)
    return df
"""
    #start = timer()
    df = TruncuatedSVD_process(tfidf_text_vectorizer, tfidf_text_vectors, df)
    #print("with TruncuatedSVD_process: ", (timer() - start) / 60, " mins")

    count_text_vectorizer = CountVectorizer(ngram_range=(1, 3), stop_words=stopwords, min_df=1, max_df=0.7)
    count_text_vectors = count_text_vectorizer.fit_transform(df["text"])
    #start = timer()
    df = LDA_process(count_text_vectorizer, count_text_vectors, df)
    #print("with LDA_process: ", (timer() - start) / 60, " mins")
    """


if __name__ == "__main__":
    # if no arguments are 'file' load data from
    # emails.csv else load from mongodb
    df_main = None
    if len(sys.argv) == 1 or sys.argv[1] == "file":
        df_main = pd.read_csv("emails.csv")
    elif sys.argv[1] == "db":
        mdb = MongoDBClient()
        df_main = mdb.get_all_messages()
    else:
        logger.error("Invalid data source should be 'file' or 'db'.")

    df_main.loc[:, "NMF_topic"] = ""

    # df_main.loc[:, "TruncatedSVD_topic"] = ""
    # df_main.loc[:, "LDA_topic"] = ""

    Number_of_Topics = 40
    Num_rows = 10
    # we will pick 3 times same number of rows in df as number_of_topics,
    # for each iteration until all rows in df are done
    total_rows = df_main.shape[0]
    logger.info("total rows = ", total_rows)
    number_of_iterations = total_rows//Num_rows
    logger.info("number of iterations = ", number_of_iterations)

    for i in range(0, number_of_iterations):
        number_of_rows = Num_rows
        if i == number_of_iterations-1:
            number_of_rows = total_rows - i*Num_rows
        df = do_for_subset(i, number_of_rows, Num_rows, df_main)
        df_main.loc[df.index, df.columns] = df

    df_main.to_csv("email_topics.csv")
    logger.info("end")


