import os
import subprocess
import logging
import shlex

from sklearn.base import TransformerMixin

from pipelines.data_types import ParseData
from en.candc2transccg import translate_candc_tree

my_logger = logging.getLogger(__name__)

class CCGSynParser(TransformerMixin):
    """Adapt C&C parser to scikit-learn transformer"""
    def __init__(self, parser_exe: str = "candc-1.00/bin/candc",
                 config_file: str = None,
                 model_path: str = "candc-1.00/models",
                 parser_printer: str = "xml",
                 log_file: str = None,
                 output_dir: str = None):
        assert os.path.exists(parser_exe)
        assert os.path.exists(model_path)

        # figure out the command to run the parser
        self.parser_exe = parser_exe
        self.parser_name = os.path.splitext(os.path.basename(parser_exe))[0]
        self.config_file = config_file
        self.model_path = model_path
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
            completed_process = subprocess.run(parse_command, check=True)
            transccg_root, encoding = translate_candc_tree(output_file, self.log_file)
            parse_data = ParseData(parse_result=transccg_root, 
                                   parse_encode=encoding,
                                   input_file=input_file,
                                   output_file=output_file)
            my_logger.debug(f"{parse_command} -> {completed_process.returncode}")
        except Exception as error:
            parse_data = ParseData(parse_error=error)
            my_logger.error(error)
        return parse_data
            
# unit test
if __name__ == "__main__":
    import lxml

    ccg_parser = CCGSynParser()
    parse_data = ccg_parser.transform("datasets/corpus_test/sentences.tok.txt")
    print(f"{parse_data}")
    assert type(parse_data.parse_result) is lxml.etree._Element
    assert parse_data.parse_encode == "UTF-8"
    assert parse_data.output_file == "datasets/corpus_test/sentences.candc.xml"
