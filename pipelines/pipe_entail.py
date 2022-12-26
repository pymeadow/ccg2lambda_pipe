"""Implement pipelines/pipeline.bash with a scikit-learn Pipeline"""

from sklearn.pipeline import Pipeline

from en.step_tokenizer import WordTokenizer
from pipelines.step_corpus_io import CorpusReader, CorpusWriter
from pipelines.step_tree_io import CCGTreeWriter
from pipelines.step_syn_parser import CCGSynParser
from pipelines.step_sem_parser import CCGSemParser
from pipelines.step_entail_prover import COQEntailmentProver
from pipelines.step_tree_visualizer import CCGTreeVisualizer

def main():
    tree_visualizer = CCGTreeVisualizer()

    # construct a reusable pipeline for different input
    basic_pipe = Pipeline([
        ("corpus_reader", CorpusReader()),
        ("en_tokenizer", WordTokenizer()),
        ("corpus_writer", CorpusWriter()),
        ("syn_parser", CCGSynParser()),
        ("syn_writer", CCGTreeWriter(output_suffix="syn.xml", output_encode=None)),
        ("syn_visual", tree_visualizer),
        ("sem_parser", CCGSemParser()),
        ("sem_writer", CCGTreeWriter(output_suffix="sem.xml")),
        ("sem_visual", tree_visualizer),
        ("entail_prover", COQEntailmentProver()),
        ("proof_writer", CCGTreeWriter(output_suffix="pro.xml")),
        ("proof_visual", tree_visualizer),
        ("pivot", "passthrough")
        ])
    
    input_file = "datasets/corpus_test/sentences.tok.txt"
    basic_pipe.set_params(corpus_writer__input_file=input_file)
    parse_data = basic_pipe.transform(input_file)
    print(f"{input_file} => {parse_data}")

main()

    