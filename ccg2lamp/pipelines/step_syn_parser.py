import os
import subprocess
import logging
import shlex

from sklearn.base import TransformerMixin

import ccg2lamp
from ccg2lamp.scripts.utils import time_count
from .data_types import ParseData
from ccg2lamp.en.candc2transccg import translate_candc_tree

my_logger = logging.getLogger(__name__)

class CCGSynParser(TransformerMixin):
    """Adapt C&C parser to scikit-learn transformer"""
    def __init__(self, config_file: str = None,
                 parser_printer: str = "xml",
                 log_file: str = None,
                 output_dir: str = None):

        # figure out the command to run the parser
        self.parser_exe = ccg2lamp.CCG2LAMP_PARSER_EXE
        self.parser_name = os.path.splitext(os.path.basename(self.parser_exe))[0]
        self.config_file = config_file
        self.model_path = ccg2lamp.CCG2LAMP_PARSER_MODEL
        self.parser_printer = parser_printer
        self.log_file = log_file
        self.output_dir = output_dir

        if self.config_file:
            config_option = f"--config {self.config_file}"
        else:
            config_option = ""
        if self.log_file:
            log_option = f"--log {self.log_file}"
        else:
            log_option = ""
        
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        # prepare the commands to run
        input_file = "{0}"
        output_file = "{1}"
        self.ccg_parse = (f"{self.parser_exe} {config_option} {log_option} " + 
                          f"--models {self.model_path} " +
                          f"--candc-printer {self.parser_printer} " +
                          f"--input {input_file} --output {output_file}")
    
    @time_count
    def transform(self, input_file: str) -> ParseData:
        """parse tokenized sentences to XML trees"""
        assert os.path.exists(input_file)

        # figure out where to save the output from the input
        input_root = os.path.basename(input_file).split(".")[0]
        
        # save the output files to a given dir or the input folder
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = os.path.dirname(input_file)

        output_file = f"{input_root}.{self.parser_name}.{self.parser_printer}"
        output_file = os.path.join(output_dir, output_file)

        # run the external parsers with the files
        parse_command = shlex.split(self.ccg_parse.format(input_file, output_file))
        try:
            completed_process = subprocess.run(parse_command, check=True, 
                                               stdout=subprocess.DEVNULL,
                                               stderr=subprocess.STDOUT)
            # transccg_root is the root element, not the entire document
            transccg_root, encoding = translate_candc_tree(output_file, self.log_file)
            parse_data = ParseData(parse_result=transccg_root, 
                                   parse_encode=encoding,
                                   input_file=input_file,
                                   output_file=output_file)
            my_logger.debug(f"{parse_command} -> {completed_process.returncode}")
        except Exception as error:
            parse_data = ParseData(parse_error=error)
            my_logger.error(str(error))
        return parse_data
            
# unit test
if __name__ == "__main__":
    import lxml
    from ccg2lamp.pipelines.step_tree_io import CCGTreeWriter
    
    logging.basicConfig(level=logging.DEBUG)

    ccg_parser = CCGSynParser()
    input_file = "datasets/corpus_test/sentences.tok.txt"
    parse_data = ccg_parser.transform(input_file)
    assert type(parse_data.parse_result) is lxml.etree._Element
    assert parse_data.parse_encode == "UTF-8"
    assert parse_data.output_file == "datasets/corpus_test/sentences.candc.xml"

    tree_writer = CCGTreeWriter(output_suffix="syn.xml", output_encode=None)
    parse_data = tree_writer.transform(parse_data)
    print(f"{input_file} => {parse_data}")
    