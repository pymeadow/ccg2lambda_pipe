"""Implement pipeline.bash with a scikit-learn Pipeline"""

from sklearn.pipeline import Pipeline

from en.pipe_tokenizer import Tokenizer
from pipelines.pipe_corpus_io import CorpusReader, CorpusWriter
from pipelines.pipe_syn_parser import CCGSynParser
from pipelines.pipe_sem_parser import CCGSemParser
from pipelines.pipe_entail_prover import COQEntailmentProver
from pipelines.pipe_tree_visualizer import CCGTreeVisualizer

def main():
    tree_visualizer = CCGTreeVisualizer()

    # construct a reusable pipeline for different input
    basic_pipe = Pipeline([
        ("corpus_reader", CorpusReader()),
        ("en_tokenizer", Tokenizer()),
        ("corpus_writer", CorpusWriter()),
        ("syn_parser", CCGSynParser()),
        ("syn_visual", tree_visualizer),
        ("sem_parser", CCGSemParser()),
        ("sem_visual", tree_visualizer),
        ("entail_prover", COQEntailmentProver()),
        ("pivot", "passthrough")
        ])
    
    input_file = "datasets/corpus_test/sentences.tok.txt"
    basic_pipe.set_params(corpus_writer__input_file=input_file)
    output_file = basic_pipe.transform(input_file)
    print(output_file)

main()

    