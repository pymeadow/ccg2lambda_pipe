"""Implement pipelines/pipeline.bash with a scikit-learn Pipeline"""

import argparse
import logging

from sklearn.pipeline import Pipeline

from ccg2lamp.pipelines.log_utils import config_log

from ccg2lamp.en.step_tokenizer import WordTokenizer
from ccg2lamp.pipelines.step_corpus_io import CorpusReader, CorpusWriter
from ccg2lamp.pipelines.step_tree_io import CCGTreeWriter
from ccg2lamp.pipelines.step_syn_parser import CCGSynParser
from ccg2lamp.pipelines.step_sem_parser import CCGSemParser
from ccg2lamp.pipelines.step_entail_prover import COQEntailmentProver
from ccg2lamp.pipelines.step_tree_visualizer import CCGTreeVisualizer

my_logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Textual Entailment Pipeline")
    parser.add_argument("--input_file", help="input corpus file", type=str)
    parser.add_argument("--nbest_output", help="nbest semantic output", type=int, default=0)
    # no, naive, spsa
    parser.add_argument("--do_abduction", help="apply abduction to entailment", type=str, default="no")
    parser.add_argument("--log_level", help="log level", type=str, default="DEBUG")
    args = parser.parse_args()
    config_log(args.log_level)

    # construct a reusable pipeline for different input
    basic_pipe = Pipeline([
        ("corpus_reader", CorpusReader()),
        ("en_tokenizer", WordTokenizer()),
        ("corpus_writer", CorpusWriter()),
        ("syn_parser", CCGSynParser()),
        ("syn_writer", CCGTreeWriter(output_suffix="syn.xml", output_encode=None)),
        ("syn_visual", CCGTreeVisualizer(output_suffix="syn")),
        ("sem_parser", CCGSemParser(nbest_output=args.nbest_output)),
        ("sem_writer", CCGTreeWriter(output_suffix="sem.xml")),
        ("sem_visual", CCGTreeVisualizer(output_suffix="sem")),
        ("entail_prover", COQEntailmentProver(do_abduction=args.do_abduction)),
        ("proof_writer", CCGTreeWriter(output_suffix="pro.xml")),
        ("proof_visual", CCGTreeVisualizer(output_suffix="pro")),
        ("pivot", "passthrough")
        ])
    
    # "datasets/corpus_test/sentences.txt"
    input_file = args.input_file
    basic_pipe.set_params(corpus_writer__input_file=input_file)
    parse_data = basic_pipe.transform(input_file)
    my_logger.info(f"{input_file} => {parse_data}")

main()

    