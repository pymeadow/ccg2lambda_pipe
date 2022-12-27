import os
from typing import List

from sklearn.base import TransformerMixin

import nltk
from nltk.tokenize import word_tokenize

class WordTokenizer(TransformerMixin):
    """NLTK tokenizer as scikit-learn transformer"""
    def __init__(self):
        nltk.data.path = os.environ['NLTK_DATA_PATH'].split(":")

    def transform(self, sentences: List[str]) -> List[List[str]]:
        return [word_tokenize(sent) for sent in sentences]


if __name__ == "__main__":
    # unit test
    # cat datasets/corpus_test/sentences.txt | python3 en/pipe_tokenizer.py
    import sys, os
    nltk_data_paths = [os.path.expanduser("~/nltk_data")]
    tokenizer = WordTokenizer(nltk_data_paths)
    sentences = [line for line in sys.stdin]
    print(tokenizer.transform(sentences))

