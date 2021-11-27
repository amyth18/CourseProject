from bs4 import BeautifulSoup
import re
from nltk import word_tokenize

import nltk
nltk.download('punkt')


def clean_text(text):
    # remove carriage return, newline and special characters.
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    text = text.replace('\r', "").replace('\n', "")
    # remove urls
    text = re.sub(r'<http(s?)://\S+>', '', text, flags=re.MULTILINE)
    text = re.sub(r"[^A-Za-z0-9\s]+", "", text)
    cleaned_text = " ".join(w for w in word_tokenize(text) if w.isalpha())
    return cleaned_text


# TODO
# remove all not ascii characters?
# remove emails addresses.
# keep tokens only in english dictionary?
def clean_text(text):
    # remove carriage return, newline and special characters.
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    text = text.replace('\r', "").replace('\n', "")
    # remove urls
    text = re.sub(r'<http(s?)://\S+>', '', text, flags=re.MULTILINE)
    return text


def extract_text_from_html(html):
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = ' '.join(chunk for chunk in chunks if chunk)
    text = clean_text(text)
    return text
