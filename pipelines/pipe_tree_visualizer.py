import os
import subprocess
import logging
import shlex

from sklearn.base import TransformerMixin

my_logger = logging.getLogger(__name__)

# map visual formats to the file extensions they produce
FORMAT_EXT = dict(plain="html", vertical="html", latex="tex")

class CCGTreeVisualizer(TransformerMixin):
    """Adapt scripts/visualizer.py to scikit-learn transformer"""
    def __init__(self, visual_exe: str = "scripts/visualize.py",
                 output_dir: str = None,
                 visual_format: str = "plain"
                 ):
        assert os.path.exists(visual_exe)
        
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        self.visual_exe = visual_exe
        self.output_dir = output_dir
        self.visual_format = f"--format {visual_format}"
        self.visual_ext = FORMAT_EXT[visual_format]
        
        input_file = "{0}"
        self.visual_command = (f"{self.visual_exe} {input_file} {self.visual_format}")

    def transform(self, input_file: str) -> str|None:
        assert os.path.exists(input_file)

        # figure out where to save the output from the input:
        input_root = os.path.splitext(os.path.basename(input_file))[0]
        
        # save the output files to a given dir or the input folder
        if self.output_dir:
            output_dir = self.output_dir
        else:
            output_dir = os.path.dirname(input_file)

        # replace the last extension by ext for the chosen format
        output_file = os.path.join(output_dir, f"{input_root}.{self.visual_ext}")
        run_command = shlex.split(f"{self.visual_command.format(input_file)}")
        try:
            with open(output_file, "w") as fp:
                completed_process = subprocess.run(run_command, check=True, stdout=fp)
                my_logger.debug(f"{run_command} -> {completed_process.returncode}")
                return output_file
        except Exception as error:
            my_logger.error(error)
            return None


# unit test
if __name__ == "__main__":
    tree_visualizer = CCGTreeVisualizer()
    output_file = tree_visualizer.transform("datasets/corpus_test/sentences.syn.xml")
    print(f"output_file={output_file}")                        
    output_file = tree_visualizer.transform("datasets/corpus_test/sentences.sem.xml")
    print(f"output_file={output_file}")                        
            
