"""Steps and utilities to read/write information from/to CCG trees"""
import os
import logging
from typing import Tuple

from sklearn.base import TransformerMixin

import lxml

from scripts.prove import serialize_tree_to_file

my_logger = logging.getLogger(__name__)

#===================================================
# Basic tree IO steps
#===================================================

class CCGTreeReader(TransformerMixin):
    """load CCG tree from file into memory"""
    def __init__(self):
        self.xml_parser = lxml.etree.XMLParser(remove_blank_text=True)
    
    def transform(self, input_file: str) -> Tuple[lxml.etree._Element, str]:
        assert os.path.exists(input_file)
        xml_tree = lxml.etree.parse(input_file, self.xml_parser)
        encoding = xml_tree.docinfo.encoding
        return xml_tree.getroot(), encoding  

class CCGTreeWriter(TransformerMixin):
    """save CCG tree in memory to output file"""
    def __init__(self, output_file=None, output_suffix=None, output_dir=None):
        """initialization"""

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        self.input_file = None
        self.output_file = output_file
        self.output_dir = output_dir
        self.output_suffix = output_suffix

    def set_params(self, input_file=None):
        """derive output file from input file"""
        assert input_file
        assert self.output_suffix

        # figure out where to save the output from the input
        input_root = os.path.basename(input_file).split(".")[0]
        
        # save the output files to a given dir or the input folder
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = os.path.dirname(input_file)
        self.output_file = os.path.join(output_dir, f"{input_root}.{self.output_suffix}")       

    def transform(self, X):
        """save xml tree to output file"""
        root_element, xml_encoding = X
        assert self.output_file
        serialize_tree_to_file(root_element, self.output_file, encoding=xml_encoding)
        # return the root for downstream steps
        return X

#===================================================
# unit test
#===================================================
if __name__ == "__main__":
    # load xml file into memory then save it back to the same file
    # use git status to check the file didn't change
    from sklearn.pipeline import Pipeline
    tree_reader = CCGTreeReader()
    tree_writer = CCGTreeWriter(output_suffix="pro.xml")
    io_pipe = Pipeline([
        ("reader", tree_reader),
        ("writer", tree_writer)])
    input_file = "datasets/corpus_test/sentences.pro.xml"
    io_pipe.set_params(writer__input_file=input_file)
    output = io_pipe.transform(input_file)
    print(output)
