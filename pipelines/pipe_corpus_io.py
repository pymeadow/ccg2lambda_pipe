from typing import List

from sklearn.base import TransformerMixin

class CorpusReader(TransformerMixin):
    """read raw corpus into memory"""
    def __init__(self, min_length: int = 1):
        self.min_length = min_length
    
    def transform(self, file_name: str) -> List[str]:
        sentences = []
        with open(file_name, "r") as input_file:
            lines = input_file.readlines()
            for line in lines:
                sent = line.strip()
                if len(sent) >= self.min_length:
                    sentences.append(sent)
        return sentences

class CorpusWriter(TransformerMixin):
    """save tokenized corpus to file"""
    def __init__(self, token_delimiter: str =" "):
        """initialization"""
        self.token_file = None
        self.token_delimiter = token_delimiter
    
    def set_params(self, token_file=None):
        self.token_file = token_file

    def transform(self, token_corpus: List[List[str]]) -> str:
        """join tokens with a delimiter into a string"""
        assert self.token_file
        with open(self.token_file, "w") as output_file:
            for token_list in token_corpus:
                token_sent = self.token_delimiter.join(token_list)
                print(token_sent, file=output_file)
        return self.token_file


# unit test
if __name__ == "__main__":
    from sklearn.pipeline import Pipeline
    from en.pipe_tokenizer import Tokenizer
    
    pipe = Pipeline([
        ("reader", CorpusReader()),
        ("tokenizer", Tokenizer()),
        ("writer", CorpusWriter()),
        ("checker", CorpusReader())])
    pipe.set_params(writer__token_file="/tmp/sentences.tok.txt")
    token_corpus = pipe.transform("datasets/corpus_test/sentences.txt")
    print(token_corpus)
