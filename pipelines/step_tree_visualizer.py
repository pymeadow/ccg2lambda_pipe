import os
import logging
import argparse
import contextlib
import dataclasses as dc
from logging import FileHandler

from sklearn.base import TransformerMixin

from pipelines.data_types import ParseData
from scripts.visualize import visualize_parse_tree

my_logger = logging.getLogger(__name__)

# map visual formats to the file extensions they produce
FORMAT_EXT = dict(plain="html", vertical="html", latex="tex")

class XMLLogHandler(FileHandler):
    """a log handler that actually saves the visual file"""
    def __init__(self, xml_tree, output_file, args):
        super().__init__(output_file)
        self.xml_tree = xml_tree
        self.args = args

    def emit(self, _record):
        # redirect the stdout to output_file
        with open(self.baseFilename, "w") as out_file:
            with contextlib.redirect_stdout(out_file):
                visualize_parse_tree(self.xml_tree, self.args)

class CCGTreeVisualizer(TransformerMixin):
    """Adapt scripts/visualizer.py to scikit-learn transformer"""
    def __init__(self, output_dir: str = None, output_suffix=None,
                 output_format: str = "plain"):
        assert output_suffix
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        self.output_dir = output_dir
        self.output_suffix = f"{output_suffix}.{FORMAT_EXT[output_format]}"

        # set up args for the visualizer
        self.args = argparse.Namespace()
        self.args.format = output_format

    def transform(self, parse_data: ParseData) -> ParseData:
        """convert XML parse tree to layout in HTML/Latex"""
        # figure out where to save the output from the input
        input_file = parse_data.input_file
        assert os.path.exists(input_file)
        input_root = os.path.basename(input_file).split(".")[0]
        
        # save the output files to a given dir or the input folder
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = os.path.dirname(input_file)

        # derive the complete output file path
        output_file = os.path.join(output_dir, f"{input_root}.{self.output_suffix}")
        self.args.trees_xml = input_file
        
        # save the visual file only if log level <= DEBUG
        xml_logger = logging.getLogger(__name__)
        xml_handler = XMLLogHandler(parse_data.parse_result, output_file, self.args)
        xml_logger.addHandler(xml_handler)
        xml_logger.debug(f"save result to {output_file}")
        
        # return a new parse data
        return dc.replace(parse_data, output_file=output_file)

# unit test
if __name__ == "__main__":
    from pipelines.step_tree_io import CCGTreeReader    
    logging.basicConfig(level=logging.DEBUG)

    tree_reader = CCGTreeReader()
    tree_visualizer = CCGTreeVisualizer(output_suffix="syn")
    
    input_file = "datasets/corpus_test/sentences.syn.xml"
    parse_data = tree_reader.transform(input_file)
    parse_data = tree_visualizer.transform(parse_data)
    print(f"{input_file} => {parse_data}")
            
