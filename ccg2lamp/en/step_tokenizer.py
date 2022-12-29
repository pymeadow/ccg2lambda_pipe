from typing import List

from sklearn.base import TransformerMixin

#import nltk
from nltk.tokenize import word_tokenize

from ccg2lamp.scripts.utils import time_count

class WordTokenizer(TransformerMixin):
    """NLTK tokenizer as scikit-learn transformer"""
    def __init__(self):
        pass

    @time_count
    def transform(self, sentences: List[str]) -> List[List[str]]:
        return [word_tokenize(sent) for sent in sentences]


if __name__ == "__main__":
    # unit test
    # cat datasets/corpus_test/sentences.txt | python en/step_tokenizer.py
    import sys
    tokenizer = WordTokenizer()
    sentences = [line for line in sys.stdin]
    print(tokenizer.transform(sentences))

