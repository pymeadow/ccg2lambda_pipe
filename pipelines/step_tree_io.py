"""Steps and utilities to read/write information from/to CCG trees"""
import os
import logging
import dataclasses as dc

from sklearn.base import TransformerMixin

import lxml

from pipelines.data_types import ParseData
from scripts.xml_utils import serialize_tree_to_file, deserialize_file_to_tree

my_logger = logging.getLogger(__name__)

#===================================================
# Basic tree IO steps
#===================================================

class CCGTreeReader(TransformerMixin):
    """load CCG tree from file into memory"""
    def __init__(self):
        self.xml_parser = lxml.etree.XMLParser(remove_blank_text=True)
    
    def transform(self, input_file: str) -> ParseData:
        assert os.path.exists(input_file)
        xml_tree = deserialize_file_to_tree(input_file)
        encoding = xml_tree.docinfo.encoding
        return ParseData(parse_result=xml_tree, 
                         parse_encode=encoding,
                         input_file=input_file) 

class CCGTreeWriter(TransformerMixin):
    """save CCG tree in memory to output file"""
    def __init__(self, output_file=None, 
                 output_suffix=None, 
                 output_dir=None, 
                 output_encode='utf-8'):
        """initialization"""
        assert output_suffix

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        self.output_file = output_file
        self.output_dir = output_dir
        self.output_suffix = output_suffix
        self.output_encode = output_encode

    def transform(self, parse_data: ParseData) -> ParseData:
        """save xml tree to output file"""
        # figure out where to save the output from the input
        if self.output_file:
            output_file = self.output_file
        else:    
            input_root = os.path.basename(parse_data.input_file).split(".")[0]
            
            # save the output files to a given dir or the input folder
            if self.output_dir:
                output_dir = self.output_dir
            else:
                output_dir = os.path.dirname(parse_data.input_file)
            output_file = os.path.join(output_dir, f"{input_root}.{self.output_suffix}")
        assert(output_file)

        if self.output_encode:
            output_encode = self.output_encode
        else:
            output_encode = parse_data.parse_encode
        assert(output_encode)

        serialize_tree_to_file(parse_data.parse_result, 
                               output_file, 
                               encoding=output_encode)
        # return a parse data object
        return dc.replace(parse_data, output_file=output_file)

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
    output = io_pipe.transform(input_file)
    print(output)
