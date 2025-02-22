
import logging
import argparse

from sklearn.base import TransformerMixin

from ccg2lamp.pipelines.data_types import ParseData

from ccg2lamp.scripts.utils import time_count
import ccg2lamp.scripts.prove as prover
from ccg2lamp.scripts.prove import prove_entail

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
        # set up parameters for the prover
        prover.ARGS = argparse.Namespace()
        prover.ARGS.abduction = do_abduction
        prover.ARGS.gold_trees = gold_trees
        prover.ARGS.timeout = timeout
        prover.ARGS.ncores = use_ncores
        prover.ARGS.print = "result"
        prover.ARGS.print_length = "full"

    @time_count
    def transform(self, parse_data: ParseData) -> ParseData:
        if parse_data.parse_result is not None:
            prove_entail(parse_data.parse_result)
        # return parse data as is because it was not changed
        return parse_data

# unit test
if __name__ == "__main__":
    from ccg2lamp.pipelines.step_tree_io import CCGTreeReader, CCGTreeWriter
    logging.basicConfig(level=logging.DEBUG)

    tree_reader = CCGTreeReader()
    input_file = "datasets/corpus_fail/entail_fail.sem.xml"
    parse_data = tree_reader.transform(input_file)
    entail_prover = COQEntailmentProver()
    parse_data = entail_prover.transform(parse_data)
    tree_writer = CCGTreeWriter(output_suffix="pro.xml")
    tree_writer.transform(parse_data)
    print(f"output_file={parse_data}")
    # use git status to check datasets/corpus_test/sentences.pro.xml