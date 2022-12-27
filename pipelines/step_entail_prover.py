import os
import logging
import argparse

import nltk
from sklearn.base import TransformerMixin

from pipelines.data_types import ParseData

import scripts.prove as prover
from scripts.prove import prove_entail

my_logger = logging.getLogger(__name__)

class COQEntailmentProver(TransformerMixin):
    """Adapt scripts/prove.py to scikit-learn transformer"""
    def __init__(self, do_abduction: str = "no",
                 gold_trees: bool = False,
                 timeout: int = 100,
                 use_ncores: int = 1):
        """initialize the prover with parameters
        Parameters:
        """
        # set up NLTK resources
        nltk.data.path = os.environ['NLTK_DATA_PATH'].split(":")
        
        # set up parameters for the prover
        prover.ARGS = argparse.Namespace()
        prover.ARGS.abduction = do_abduction
        prover.ARGS.gold_trees = gold_trees
        prover.ARGS.timeout = timeout
        prover.ARGS.ncores = use_ncores
        prover.ARGS.print = "result"
        prover.ARGS.print_length = "full"

    def transform(self, parse_data: ParseData) -> ParseData:
        prove_entail(parse_data.parse_result)
        # return parse data as is because it was not changed
        return parse_data

# unit test
if __name__ == "__main__":
    from pipelines.step_tree_io import CCGTreeReader, CCGTreeWriter
    tree_reader = CCGTreeReader()
    input_file = "datasets/corpus_test/sentences.sem.xml"
    parse_data = tree_reader.transform(input_file)
    entail_prover = COQEntailmentProver()
    parse_data = entail_prover.transform(parse_data)
    tree_writer = CCGTreeWriter(output_suffix="pro.xml")
    tree_writer.transform(parse_data)
    print(f"output_file={parse_data}")