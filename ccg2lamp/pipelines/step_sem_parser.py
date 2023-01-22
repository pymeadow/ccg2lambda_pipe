import logging
import argparse

from sklearn.base import TransformerMixin

import ccg2lamp
from ccg2lamp.scripts.utils import time_count
import ccg2lamp.scripts.semparse as semparse
from ccg2lamp.scripts.semparse import sem_parse

from ccg2lamp.pipelines.data_types import ParseData

my_logger = logging.getLogger(__name__)

class CCGSemParser(TransformerMixin):
    """Adapt scripts/semparse.py to scikit-learn transformer"""
    def __init__(self, arbitrary_types: bool = False, # for --arbi-types
                 gold_trees: bool = False, # for --gold-trees
                 nbest_output: int = 0, # for --nbest
                 use_ncores: int = 3 # for --ncores
                 ):
        
        self.model_path = ccg2lamp.CCG2LAMP_SEM_TEMPLATE
        
        # set up the global parameters for the semantic parser
        semparse.ARGS = argparse.Namespace()
        semparse.ARGS.templates = self.model_path
        semparse.ARGS.arbi_types = arbitrary_types
        semparse.ARGS.gold_trees = gold_trees
        semparse.ARGS.nbest = nbest_output
        semparse.ARGS.ncores = use_ncores
    
    @time_count
    def transform(self, parse_data: ParseData) -> ParseData:
        # this will extend the parse tree with semantic nodes
        if parse_data.parse_result is not None:
            sem_parse(parse_data.parse_result)
        # so we can just return the parse data as is
        return parse_data

# unit test
if __name__ == "__main__":
    from ccg2lamp.pipelines.step_tree_io import CCGTreeReader, CCGTreeWriter
    
    logging.basicConfig(level=logging.DEBUG)

    tree_reader = CCGTreeReader()
    tree_writer = CCGTreeWriter(output_suffix="sem.xml", output_encode="utf-8")
    parse_data = tree_reader.transform("datasets/corpus_fail/sem_fail.syn.xml")
    sem_parser = CCGSemParser(use_ncores=0)   
    parse_data = sem_parser.transform(parse_data)
    output = tree_writer.transform(parse_data)
    print("output=", output)
    assert output.output_file == "datasets/corpus_test/sentences.sem.xml"                      
            
        