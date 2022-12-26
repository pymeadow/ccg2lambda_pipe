import os
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
    """save tokenized corpus to output file derived from input file"""
    def __init__(self, output_dir:str = None, 
                 token_delimiter: str =" ",
                 output_suffix="tok.txt"):
        """initialization"""
        self.output_dir = output_dir
        self.output_file = None
        self.token_delimiter = token_delimiter
        self.output_suffix = output_suffix

    def set_params(self, input_file=None):
        """derive output file from input file"""
        self.input_file = input_file

        # figure out where to save the output from the input
        input_root = os.path.basename(input_file).split(".")[0]

        # save the output file to a given dir or the input folder
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = os.path.dirname(input_file)
        self.output_file = os.path.join(output_dir, f"{input_root}.{self.output_suffix}")
        

    def transform(self, token_corpus: List[List[str]]) -> str:
        """join tokens and save them to the output file"""
        assert self.output_file
        with open(self.output_file, "w") as output_file:
            for token_list in token_corpus:
                token_sent = self.token_delimiter.join(token_list)
                print(token_sent, file=output_file)
        return self.output_file


# unit test
if __name__ == "__main__":
    from sklearn.pipeline import Pipeline
    from en.step_tokenizer import WordTokenizer
    
    pipe = Pipeline([
        ("reader", CorpusReader()),
        ("tokenizer", WordTokenizer()),
        ("writer", CorpusWriter()),
        ("checker", CorpusReader())])
    input_file = "datasets/corpus_test/sentences.txt"
    pipe.set_params(writer__input_file=input_file)
    output_file = pipe.transform(input_file)
    print(output_file)
