import os
import subprocess
import logging
import shlex

from sklearn.base import TransformerMixin

my_logger = logging.getLogger(__name__)

class COQEntailmentProver(TransformerMixin):
    """Adapt scripts/prove.py to scikit-learn transformer"""
    def __init__(self, prover_exe: str = "scripts/prove.py",
                 nltk_data_paths: list = ["~/nltk_data"],
                 coq_lib_path: str = "./coq_entail/coqlib.v",
                 output_dir: str = None,
                 do_abduction: str = "no",
                 gold_trees: bool = False,
                 print_output: str = "result",
                 print_length: str = "full",
                 timeout: int = 100,
                 use_ncores: int = 1):
        """initialize the prover with parameters
        Parameters:
            nltk_data_paths: 
                specify the wordnet and owm files for abduction
            coq_lib_path: 
                specify the path to coqlib.v file used 
                by scripts/semantic_types
        """
        assert os.path.exists(prover_exe)
        for path in nltk_data_paths:
            assert os.path.exists(os.path.expanduser(path))
        assert os.path.exists(coq_lib_path)

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        self.prover_exe = prover_exe
        self.nltk_data_paths = nltk_data_paths
        self.coq_lib_path = coq_lib_path
        self.output_dir = output_dir
        self.do_abduction = f"--abduction {do_abduction}"
        self.gold_trees = f"--gold_trees" if gold_trees else ""
        self.print_output = f"--print {print_output}"
        self.print_length = f"--print_length {print_length}"
        self.timeout = f"--timeout {timeout}"
        self.use_ncores = f"--ncores {use_ncores}"
        input_file = "{0}"
        output_file = "{1}"
        output_html = "{2}"
        self.prove_command = (f"{self.prover_exe} {input_file} " +
                              f"{self.do_abduction} {self.gold_trees} " +
                              f"{self.print_output} {self.print_length} " +
                              f"{self.timeout} {self.use_ncores} " +
                              f"--proof {output_file} --graph_out {output_html}")
        
        # pass environment variables to external prover process
        # which then passes them to the coqtop process
        prove_env = dict(NLTK_DATA_PATH=":".join(self.nltk_data_paths),
                         COQ_LIB_PATH=self.coq_lib_path, 
                         COQPATH=os.path.dirname(self.coq_lib_path))
        self.run_env = os.environ.update(prove_env)

    def transform(self, input_file: str) -> str|None:
        assert os.path.exists(input_file)

        # figure out where to save the output from the input
        input_root = os.path.basename(input_file).split(".")[0]
        
        # save the output files to a given dir or the input folder
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = os.path.dirname(input_file)
        output_file = os.path.join(output_dir, f"{input_root}.pro.xml")
        output_html = os.path.join(output_dir, f"{input_root}.pro.html")
        run_command = shlex.split(f"{self.prove_command.format(input_file, output_file, output_html)}")
        try:
            completed_process = subprocess.run(run_command, env=self.run_env, check=True)
            my_logger.debug(f"{run_command} -> {completed_process.returncode}")
            return output_file
        except Exception as error:
            my_logger.error(error)
            return None

# unit test
if __name__ == "__main__":
    entail_prover = COQEntailmentProver(nltk_data_paths=["~/nltk_data"],
                                        coq_lib_path="./coq_entail/coqlib.v")
    output_file = entail_prover.transform("datasets/corpus_test/sentences.sem.xml")
    print(f"output_file={output_file}")