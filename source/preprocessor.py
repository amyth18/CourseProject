import re
import unicodedata
import nltk
import contractions
import inflect
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer


nltk.download('stopwords')
nltk.download('punkt')

ACCESS_TOKEN_FILE = "token.pickle"


def replace_contractions(text):
    return contractions.fix(text)


def remove_urls(sample):
    return re.sub(r"http\S+", "", sample)


def remove_non_ascii(words):
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode(
            'ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words


def to_lowercase(words):
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words


def remove_punctuation(words):
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', ' ', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words


def replace_spaces(text):
    return re.sub(r'\s\s+', ' ', text)


def replace_numbers(words):
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words


def remove_stopwords(words):
    new_words = []
    for word in words:
        if word not in stopwords.words('english'):
            new_words.append(word)
    return new_words


def stem_words(words):
    stemmer = LancasterStemmer()
    stems = []
    for word in words:
        stem = stemmer.stem(word)
        stems.append(stem)
    return stems


def lemmatize_verbs(words):
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)
    return lemmas


def normalize(words):
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = replace_numbers(words)
    words = remove_stopwords(words)
    return words


def preprocess_text(sample):
    sample = remove_urls(sample)
    sample = replace_contractions(sample)
    words = nltk.word_tokenize(sample)
    words = normalize(words)
    text = " ".join(words)
    return replace_spaces(text)


def preprocess_html(html):
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    # get text
    text = soup.get_text(" ")
    # logger.debug(f"Text from BS: {text}")
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = ' '.join(chunk for chunk in chunks if chunk)
    text = preprocess_text(text)
    return text


if __name__ == "__main__":
    import sys
    from gmail_client import GmailClient

    gmc = GmailClient()
    if sys.argv[1] == 'l':
        gmc.list_labels()
        print(gmc.list_labels())
    elif sys.argv[1] == 's':
        label_ids = list()
        label_ids.append(sys.argv[2])
        print(label_ids)
        msg_list = gmc.list_mails_with_subjects_only(label_ids=label_ids)
        print(msg_list)
    else:
        msg_id = sys.argv[2]
        print(msg_id)
        msg = gmc.get_message(msg_id=msg_id)
        print(msg)

