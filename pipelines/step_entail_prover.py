import os
import logging
import argparse

from sklearn.base import TransformerMixin

from pipelines.data_types import ParseData

import scripts.prove as prover
from scripts.prove import prove_entail

my_logger = logging.getLogger(__name__)

class COQEntailmentProver(TransformerMixin):
    """Adapt scripts/prove.py to scikit-learn transformer"""
    def __init__(self, nltk_data_paths: list = ["~/nltk_data"],
                 coq_lib_path: str = "./coq_entail/coqlib.v",
                 do_abduction: str = "no",
                 gold_trees: bool = False,
                 timeout: int = 100,
                 use_ncores: int = 1):
        """initialize the prover with parameters
        Parameters:
            nltk_data_paths: 
                specify the wordnet and owm files for abduction
            coq_lib_path: 
                specify the path to coqlib.v file used 
                by scripts/semantic_types
        """
        for path in nltk_data_paths:
            assert os.path.exists(os.path.expanduser(path))
        assert os.path.exists(coq_lib_path)

        self.nltk_data_paths = nltk_data_paths
        self.coq_lib_path = coq_lib_path
        
        # set up parameters for the prover
        prover.ARGS = argparse.Namespace()
        prover.ARGS.abduction = do_abduction
        prover.ARGS.gold_trees = gold_trees
        prover.ARGS.timeout = timeout
        prover.ARGS.ncores = use_ncores
        prover.ARGS.print = "result"
        prover.ARGS.print_length = "full"
        
        # update environment variables for the prover and the coqtop process
        prove_env = dict(NLTK_DATA_PATH=":".join(self.nltk_data_paths),
                         COQ_LIB_PATH=self.coq_lib_path, 
                         COQPATH=os.path.dirname(self.coq_lib_path))
        os.environ.update(prove_env)

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
    entail_prover = COQEntailmentProver(nltk_data_paths=["~/nltk_data"],
                                        coq_lib_path="./coq_entail/coqlib.v")
    parse_data = entail_prover.transform(parse_data)
    tree_writer = CCGTreeWriter(output_suffix="pro.xml")
    tree_writer.transform(parse_data)
    print(f"output_file={parse_data}")