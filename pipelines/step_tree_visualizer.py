import os
import logging
import argparse
import contextlib
import dataclasses as dc

from sklearn.base import TransformerMixin

from pipelines.data_types import ParseData
from scripts.visualize import visualize_parse_tree

my_logger = logging.getLogger(__name__)

# map visual formats to the file extensions they produce
FORMAT_EXT = dict(plain="html", vertical="html", latex="tex")

class CCGTreeVisualizer(TransformerMixin):
    """Adapt scripts/visualizer.py to scikit-learn transformer"""
    def __init__(self, output_dir: str = None, visual_format: str = "plain"):
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        self.output_dir = output_dir
        self.output_suffix = FORMAT_EXT[visual_format]

        self.args = argparse.Namespace()
        self.args.format = visual_format

    def transform(self, parse_data: ParseData) -> ParseData:
        """convert XML parse tree to layout in HTML/Latex"""
        # always use the output_file to derive the visual file
        input_file = parse_data.output_file
        assert os.path.exists(input_file)

        # figure out where to save the output from the input:
        input_root = os.path.splitext(os.path.basename(input_file))[0]
        
        # save the output files to a given dir or the input folder
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = os.path.dirname(input_file)

        # replace the last extension by ext for the chosen format
        output_file = os.path.join(output_dir, f"{input_root}.{self.output_suffix}")
        self.args.trees_xml = input_file
        # redirect the stdout to output_file
        with open(output_file, "w") as out_file:
            with contextlib.redirect_stdout(out_file):
                visualize_parse_tree(parse_data.parse_result, self.args)
        
        # return a new parse data
        return dc.replace(parse_data, output_file=output_file)

# unit test
if __name__ == "__main__":
    from pipelines.step_tree_io import CCGTreeReader
    tree_reader = CCGTreeReader()
    tree_visualizer = CCGTreeVisualizer()
    
    for input_file in ["datasets/corpus_test/sentences.syn.xml", 
                       "datasets/corpus_test/sentences.sem.xml"]:
        parse_data = tree_reader.transform(input_file)
        parse_data = tree_visualizer.transform(parse_data)
        print(f"{input_file} => {parse_data}")
            
