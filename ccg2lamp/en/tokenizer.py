
from nltk.tokenize import word_tokenize

class Tokenizer():
    def __init__(self):
        pass
    
    def transform(self, sentence):
        return word_tokenize(sentence)
    
if __name__ == "__main__":
    import sys
    tokenizer = Tokenizer()
    for line in sys.stdin:
        tokens = " ".join(tokenizer.transform(line.strip()))
        print(tokens)

