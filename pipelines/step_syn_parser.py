import os
import subprocess
import logging
import shlex
from typing import Tuple

from sklearn.base import TransformerMixin

my_logger = logging.getLogger(__name__)

class CCGSynParser(TransformerMixin):
    """Adapt C&C parser to scikit-learn transformer"""
    def __init__(self, parser_exe: str = "candc-1.00/bin/candc",
                 config_file: str = None,
                 model_path: str = "candc-1.00/models",
                 parser_printer: str = "xml",
                 parser_log_file: str = None,
                 output_dir: str = None):
        assert os.path.exists(parser_exe)
        assert os.path.exists(model_path)

        # figure out the command to run the parser
        self.parser_exe = parser_exe
        self.parser_name = os.path.splitext(os.path.basename(parser_exe))[0]
        self.config_file = config_file
        self.model_path = model_path
        self.parser_printer = parser_printer
        self.parser_log_file = parser_log_file
        self.output_dir = output_dir

        if self.config_file:
            config_option = f"--config {self.config_file}"
        else:
            config_option = ""
        if self.parser_log_file:
            log_option = f"--log {self.parser_log_file}"
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
                 
    def transform(self, input_file: str) -> Tuple[str, str|None]|None:
        """parse tokenized sentences to XML file"""
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
            completed_process = subprocess.run(parse_command, check=True)
            my_logger.debug(f"{parse_command} -> {completed_process.returncode}")
            return (output_file, self.parser_log_file) 
        except Exception as error:
            my_logger.error(error)
            return None
            
# unit test
if __name__ == "__main__":
    ccg_parser = CCGSynParser()
    output_file, log_file = ccg_parser.transform("datasets/corpus_test/sentences.tok.txt")
    print(f"output_file={output_file}")
    assert output_file == "datasets/corpus_test/sentences.candc.xml"
