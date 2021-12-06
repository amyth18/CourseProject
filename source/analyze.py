from gensim import corpora
from gensim import models
from gensim.models import Phrases

from pprint import pprint
from mongo_client import MongoDBClient


mdb = MongoDBClient()
df = mdb.get_all_messages()
df.loc[df.text == "", 'text'] = df.loc[df.text == ""]['subject']
df.loc[df.text.isna(), 'text'] = df[df.text.isna()]['subject']
emails = df['text'].tolist()

# Remove numbers, but not words that contain numbers.
emails = [[token for token in email if not token.isnumeric()] for email in emails]
# Remove words that are only one character.
emails = [[token for token in email if len(token) > 1] for email in emails]

bigram = Phrases(emails, min_count=20)
for idx in range(len(emails)):
    for token in bigram[emails[idx]]:
        if '_' in token:
            # Token is a bigram, add to document.
            emails[idx].append(token)


dictionary = corpora.Dictionary(emails)
corpus = [dictionary.doc2bow(text) for text in texts]
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]

lda_model = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=2)
top_topics = lda_model.top_topics(corpus)
print(len(top_topics))
pprint(top_topics)
