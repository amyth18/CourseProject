from gensim import models
from gensim.models import Phrases
from nltk.tokenize import RegexpTokenizer
from gensim.corpora import Dictionary
from gensim.models import LdaModel

from mongo_client import MongoDBClient
from logger import logger


class TopicModel:
    def __init__(self):
        self._mdb = MongoDBClient()
        self._tokenized_emails = list()
        self._msg_ids = None
        self._model = None

    def _load_messages(self):
        # TODO test only with 100 message first.
        df = self._mdb.get_all_messages()
        df.loc[df.text == "", 'text'] = df.loc[df.text == ""]['subject']
        df.loc[df.text.isna(), 'text'] = df[df.text.isna()]['subject']
        emails = df['text'].tolist()
        print(emails)
        # Split the documents into tokens.
        tokenizer = RegexpTokenizer(r'\w+')
        for idx in range(len(emails)):
            emails[idx] = tokenizer.tokenize(emails[idx])  # Split into words.
            # Remove numbers, but not words that contain numbers.
        emails = [[token for token in email if not token.isnumeric()] for email in emails]
        # Remove words that are only one character.
        emails = [[token for token in email if len(token) > 3] for email in emails]
        # add bi-grams to document vector.
        bigram = Phrases(emails, min_count=20)
        for idx in range(len(emails)):
            for token in bigram[emails[idx]]:
                if '_' in token:
                    # Token is a bigram, add to document.
                    emails[idx].append(token)
        self._tokenized_emails = emails
        self._msg_ids = df['_id'].tolist()

    def _save_topics(self, top_topics):
        topic_list = list()
        for idx, topic in enumerate(top_topics):
            topic_words = topic[0]
            topic = {
                "topic": "topic_" + str(idx),
                "words": list()
            }
            for word_prob in topic_words[1:10]:
                (prob, word) = word_prob
                topic["words"].append(word)
            topic_list.append(topic)
        # save to DB.
        logger.info(topic_list)
        for topic in topic_list:
            self._mdb.get_db_handle().topics.replace_one(
                    {"_id": topic['topic']},
                    topic,
                    upsert=True
            )

    def _update_email_topics(self, email_topics):
        for idx, email_topic in enumerate(email_topics):
            topics = list()
            for topic_prob in email_topic:
                tid, prob = topic_prob
                # we assign topic to email only if prob >= 0.3
                # ToDo check if this works well?
                if prob >= 0.3:
                    topics.append("topic_"+str(tid))
                msg_id = self._msg_ids[idx]
                self._mdb.get_db_handle().emails.update_one(
                    {'_id': msg_id},
                    {
                        '$set': {
                            'topics': topics
                        }
                    }
                )

    def discover(self):
        self._load_messages()
        # Create a dictionary representation of the documents.
        dictionary = Dictionary(self._tokenized_emails)
        # Filter out words that occur less than 1% documents, or more than 50% of the documents.
        lower_cut_off = int(len(self._tokenized_emails) * 0.1)
        dictionary.filter_extremes(no_below=lower_cut_off, no_above=0.5)
        # Bag-of-words representation of the documents.
        corpus = [dictionary.doc2bow(email) for email in self._tokenized_emails]
        # use TF-IDF transformation
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        # Set training parameters.
        num_topics = 8
        chunksize = 2000
        passes = 100
        iterations = 1000
        eval_every = None  # Don't evaluate model perplexity, takes too much time.
        # Make a index to word dictionary.
        temp = dictionary[0]  # This is only to "load" the dictionary.
        id2word = dictionary.id2token
        # train the model
        self._model = LdaModel(
            corpus=corpus_tfidf,
            id2word=id2word,
            chunksize=chunksize,
            alpha='auto',
            eta='auto',
            iterations=iterations,
            num_topics=num_topics,
            passes=passes,
            eval_every=eval_every
        )
        top_topics = self._model.top_topics(corpus)
        logger.info(top_topics)
        self._save_topics(top_topics)
        email_topics = self._model[corpus_tfidf]
        self._update_email_topics(email_topics)
        avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
        logger.info('Average topic coherence: %.4f.' % avg_topic_coherence)


if __name__ == "__main__":
    tpm = TopicModel()
    tpm.discover()

