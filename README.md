# 0 Introduction

This repository adapts [the original Python scripts](./ORIG_README.md) to [Scikit-Learn transformers](https://scikit-learn.org/stable/modules/generated/sklearn.base.TransformerMixin.html) that 
can be configured and composed into different [Pipelines](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html).

A working Scikit-Learn pipeline can be found [here](./tests/pipe_entail.py).

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

    input_file = args.input_file
    basic_pipe.set_params(corpus_writer__input_file=input_file)
    parse_data = basic_pipe.transform(input_file)
```

The pipeline accepts an input file of sentences, and produces a [parse data](ccg2lamp/pipelines/data_types.py) that contains sentence tokens, CCG parse tree, logic formulas, and COQ proof scripts.

The pipeline also saves the intermediate results in various XML and HTML files, as the original Python scripts do, by the inserted writer steps.

The writer steps are optional, and they are controlled by the global logging level. 
They are turned off if the logging level is greater than DEBUG.

The pipeline produces the same results as [the bash script](./tests/pipe_entail.bash), but 
it runs ~3.5x faster.

The bottleneck of the pipeline is the C&C CCG parser, which is a Linux executable that accepts and produces files.

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

python -m venv ../../py_environs/ccg2lambda
source ../../py_environs/ccg2lambda/bin/activate

pip install -r requirements.txt
```

Download the NLTK resources for English:

```
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt')"
cd ~/nltk_data/tokenizer
/usr/bin/unzip punkt.zip
```

Note that you don't have to unzip the `wordnet` or `omw-1.4` files, as the relevant NLTK modules can work with them.

By default, these resource files are saved under folder `~/nltk_data`.
Please set environment variable [NLTK_DATA](https://www.nltk.org/data.html), if necessary, so the pipeline can find the resources. 

## 1.3 Install COQ

```
sudo apt-get install coq
coqc --version
The Coq Proof Assistant, version 8.6 (October 2017)
compiled on Oct 28 2017 14:23:55 with OCaml 4.05.0
```

`resources/coq_entail/coqlib.vo` was compiled by `cogc` and is ready to use by `coqtop`.


## 1.4 Install C&C Parser

```
./ccg2lamp/en/install_candc.sh
```

# 2 Validation Tests

## 2.1 Original tests

```
python -m ccg2lamp.scripts.run_tests

----------------------------------------------------------------------
Ran 162 tests in 1.342s

OK (expected failures=3)

```

## 2.2 Bash Pipeline

Run the bash pipeline on the test corpus to reproduce [the original results](./ORIG_README.md):

```
./tests/pip_entail.bash datasets/corpus_test/sentences.txt
yes

git status
# no file in datasets/corpus_test/ is changed
```

## 2.3 Scikit-Learn Pipeline

Run the scikit-learn pipeline on the same input to produce identical results as the bash pipeline:

```
PYTHONPATH=. python tests/pipe_entail.py --input_file datasets/corpus_test/sentences.txt
yes

git status
# no file in datasets/corpus_test/ is changed
```

