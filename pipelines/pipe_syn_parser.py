import os
import subprocess
import logging
import shlex

from sklearn.base import TransformerMixin

my_logger = logging.getLogger(__name__)

class CCGSynParser(TransformerMixin):
    """Adapt C&C parser to scikit-learn transformer"""
    def __init__(self, parser_exe: str = "candc-1.00/bin/candc",
                 config_file: str = None,
                 model_path: str = "candc-1.00/models",
                 parser_printer: str = "xml",
                 parser_log_file: str = None,
                 trans_exe: str = "en/candc2transccg.py",
                 output_dir: str = None):
        assert os.path.exists(parser_exe)
        assert os.path.exists(model_path)
        assert os.path.exists(trans_exe)

        # resolve the absolute path to the executable
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
        self.trans_exe = trans_exe
        if self.parser_log_file:
            log_option = f"--log {self.parser_log_file}"
            log_arg = self.parser_log_file
        else:
            log_option = ""
            log_arg = ""
        
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        # prepare the commands to run
        self.ccg_parse = (f"{self.parser_exe} {config_option} {log_option} " + 
                          f"--models {self.model_path} " +
                          f"--candc-printer {self.parser_printer} ")
        # to be replaced by the output file from C&C
        place_holder = "{0}"
        self.ccg_trans = f"{self.trans_exe} {place_holder} {log_arg}"
                 
    def transform(self, input_file: str) -> str|None:
        """parse tokenized input_file to CCG tree XML file"""
        assert os.path.exists(input_file)

        # figure out where to save the output from the input
        input_root = os.path.basename(input_file).split(".")[0]
        
        # save the output files to a given dir or the input folder
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = os.path.dirname(input_file)

        parser_file = f"{input_root}.{self.parser_name}.{self.parser_printer}"
        parser_path = os.path.join(output_dir, parser_file)
        parse_output = os.path.join(output_dir, f"{input_root}.syn.xml")

        # run the external parsers with the files
        parse_command = shlex.split(self.ccg_parse + f"--input {input_file} --output {parser_path}")
        trans_command = shlex.split(f"{self.ccg_trans.format(parser_path)}")
        try:
            completed_process = subprocess.run(parse_command, check=True)
            my_logger.debug(f"{parse_command} -> {completed_process.returncode}")
            with open(parse_output, "w") as out_file:
                completed_process = subprocess.run(trans_command, stdout=out_file, check=True)
                my_logger.debug(f"{trans_command} -> {completed_process.returncode}")
            return parse_output
        except Exception as error:
            my_logger.error(error)
            return None
            
# unit test
if __name__ == "__main__":
    # python pipelines/pipe_ccg_parser.py
    ccg_parser = CCGSynParser()
    output_file = ccg_parser.transform("datasets/corpus_test/sentences.tok.txt")
    print(f"output_file={output_file}")
