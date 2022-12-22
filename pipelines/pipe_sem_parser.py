import os
import subprocess
import logging
import shlex

from sklearn.base import TransformerMixin

my_logger = logging.getLogger(__name__)

class CCGSemParser(TransformerMixin):
    """Adapt scripts/semparse.py to scikit-learn transformer"""
    def __init__(self, parser_exe: str = "scripts/semparse.py",
                 model_path: str = "en/semantic_templates_en_emnlp2015.yaml",
                 output_dir: str = None,

                 arbitrary_types: bool = False, # for --arbi-types
                 gold_trees: bool = False, # for --gold-trees
                 nbest_output: int = 0, # for --nbest
                 use_ncores: int = 3 # for --ncores
                 ):
        assert os.path.exists(parser_exe)
        assert os.path.exists(model_path)
        
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        self.parser_exe = parser_exe
        self.model_path = model_path
        self.output_dir = output_dir
        
        self.arbi_types = "--arbi-types" if arbitrary_types else ""
        self.gold_trees = "--gold-trees" if gold_trees else ""
        self.nbest_output = f"--nbest {nbest_output}"
        self.use_ncores = f"--ncores {use_ncores}"
        
        input_file = "{0}"
        output_file = "{1}"
        self.parse_command = (f"{self.parser_exe} {self.arbi_types} {self.gold_trees} " +
                              f"{self.nbest_output} {self.use_ncores} " +
                              f"{input_file} {model_path} {output_file}")

    def transform(self, input_file: str) -> str|None:
        assert os.path.exists(input_file)

        # figure out where to save the output from the input
        input_root = os.path.basename(input_file).split(".")[0]
        
        # save the output files to a given dir or the input folder
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = os.path.dirname(input_file)
        output_file = os.path.join(output_dir, f"{input_root}.sem.xml")
        run_command = shlex.split(f"{self.parse_command.format(input_file, output_file)}")
        try:
            completed_process = subprocess.run(run_command, check=True)
            my_logger.debug(f"{run_command} -> {completed_process.returncode}")
            return output_file
        except Exception as error:
            my_logger.error(error)
            return None


# unit test
if __name__ == "__main__":
    sem_parser = CCGSemParser()
    output_file = sem_parser.transform("datasets/corpus_test/sentences.syn.xml")
    print(f"output_file={output_file}")                        
            
        