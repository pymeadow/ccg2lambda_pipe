# 0 Architecture

This repository made the following improvements to [the original architecture](./ORIG_README.md):
* Adapted the original file-based Python programs to memory-based scikit-learn Pipelines
* Peplaced hard-coded dependences on external NLTK or COG resources with environment variables
* Upgraded the code base to Python 3.10

A working scikit-learn pipeline can be found [here](./pipelines/pipe_entail.py).

```
    basic_pipe = Pipeline([
        ("corpus_reader", CorpusReader()),
        ("en_tokenizer", WordTokenizer()),
        ("corpus_writer", CorpusWriter()),
        ("syn_parser", CCGSynParser()),
        ("syn_writer", CCGTreeWriter(output_suffix="syn.xml", output_encode=None)),
        ("syn_visual", CCGTreeVisualizer(output_suffix="syn")),
        ("sem_parser", CCGSemParser()),
        ("sem_writer", CCGTreeWriter(output_suffix="sem.xml")),
        ("sem_visual", CCGTreeVisualizer(output_suffix="sem")),
        ("entail_prover", COQEntailmentProver()),
        ("proof_writer", CCGTreeWriter(output_suffix="pro.xml")),
        ("proof_visual", CCGTreeVisualizer(output_suffix="pro")),
        ("pivot", "passthrough")
        ])
```

This pipeline produces the same results as [the bash script](./pipelines/pipe_entail.bash), but 
it runs ~3.5x faster.

The bottleneck of the pipeline is the C&C CCG parser, which is still file based, because we don't have its
source code.

# 1 Installation

* Ubuntu 18.04
* git version 2.17.1 
* Python 3.10.8
* pip 22.2.2

## 1.1 Prerequisites

```
sudo apt-get install libxml2-dev libxslt1-dev
sudo apt-get install python3.10-venv
sudo apt-get install zip unzip
```

## 1.2 Install CCG2Lambda

Install the repository and dependences into a Python virtual environment:

```
git clone git@github.com:pymeadow/ccg2lambda_pipe.git

python3 -m venv ../../py_environs/ccg2lambda
source ../../py_environs/ccg2lambda/bin/activate

pip3 install -r requirements.txt
```

Download NLTK resources for English:

```
python3 -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt')"
cd ~/nltk_data/tokenizer
/usr/bin/unzip punkt.zip
```

Note that you don't have to unzip wordnet or omw, as the relevant NLTK API can work with zip files.

By default, these resource files are saved under folder `~/nltk_data`.
You can move these files to different folder.

## 1.3 Install COQ

```
sudo apt-get install coq
coqc --version
The Coq Proof Assistant, version 8.6 (October 2017)
compiled on Oct 28 2017 14:23:55 with OCaml 4.05.0
```

Move file `coqlib.v` that contains the tactics for textual entailment to a folder you choose:

```
mkdir coq_entail
mv coqlib.v coq_entail
```

Compile `coqlib.v` to a COQ module that can be loaded by `coqtop`:

```
coqc coq_entail/coqlib.v

ls -l coq_entail
12146 coqlib.glob
21217 coqlib.vo
1316  .coqlib.vo.aux
```

## 1.4 Install C&C Parser

```
./en/install_candc.sh
Setting en/parser_location.txt pointing to .../ccg2lambda_pipe/candc-1.00
```

# 2 Validation Tests

Make necessary changes to the environment variables in [the bash pipeline](pipelines/pipeline.bash), if 
you chose different NLTK or COG folders than described above.

Then run it on the test corpus to reproduce [the original results](./ORIG_README.md):

```
pipelines/pip_entail.bash datasets/corpus_test/sentences.txt
yes

git status
# no file in datasets/corpus_test/ is changed
```

Run the scikit-learn pipeline on the same input to produce identical results as the bash pipeline:

```
python pipelines/pipe_entail.py --input_file datasets/corpus_test/sentences.txt
yes

git status
# no file in datasets/corpus_test/ is changed
```

