# 0 Introduction

This repository made the following improvements to the [the original ccg2lambda](./ORIG_README.md).

## 0.1 Scikit-Learn Pipelines
The original Python programs were adapted
to [Scikit-Learn transformers](https://scikit-learn.org/stable/modules/generated/sklearn.base.TransformerMixin.html) such that 
they can be configured and composed through an uniform interface.

[This example](./tests/pipe_entail.py) illustrates they can be composed into a [Scikit-Learn Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html):

```
    basic_pipe = Pipeline([
        ("corpus_reader", CorpusReader()),
        ("en_tokenizer", WordTokenizer()),
        ("syn_parser", CCGSynParser()),
        ("syn_writer", CCGTreeWriter(output_suffix="syn.xml", output_encode=None)),
        ("syn_visual", CCGTreeVisualizer(output_suffix="syn")),
        ("sem_parser", CCGSemParser(nbest_output=args.nbest_output)),
        ("sem_writer", CCGTreeWriter(output_suffix="sem.xml")),
        ("sem_visual", CCGTreeVisualizer(output_suffix="sem")),
        ("entail_prover", COQEntailmentProver(do_abduction=args.do_abduction)),
        ("proof_writer", CCGTreeWriter(output_suffix="pro.xml")),
        ("proof_visual", CCGTreeVisualizer(output_suffix="pro")),
        ("pivot", "passthrough")
        ])

    input_file = args.input_file
    basic_pipe.set_params(syn_parser__input_file=input_file)
    parse_data = basic_pipe.transform(input_file)
```

The pipeline accepts an input file of sentences, and produces [parse data](ccg2lamp/pipelines/data_types.py) that contain sentence tokens, CCG parse tree, logic formulas, and COQ proof scripts.

The pipeline saves the intermediate XML and HTML files derived from the input file with the writer steps.

The writer steps are controlled by the global logging level. 
They are turned off if the logging level is greater than DEBUG.

The pipeline produces the same files as [the bash script](./tests/pipe_entail.bash), but 
it runs ~3.5x faster.

The bottleneck of the pipeline is the C&C CCG parser, which is a Linux executable that accepts and produces files.

A pipeline can be constructed from a Python dictionary or a json file by a PipeFactory, as illustrated in [this example](ccg2lamp/pipelines/pipe_factory.py).

## 0.2 Partial Semantics
The semantic analysis component was enhanced to return partial logic formulas, when a complete semantic analysis fails.

A partial logic formula consists of a list of well-formed logic formulas (fragments) that cannot be composed into well-formed formulas.

Some examples of partial analyses can be found at [here](https://htmlpreview.github.io/?https://github.com/pymeadow/ccg2lambda_pipe/blob/recover_partial_semantics/datasets/corpus_fail/sem_fail.sem.html).

# 1 Installation

You can either use docker or install all the requirements on your local machine.

## Running on docker
Clone the repository and run the docker with commands like these:
```shell
git clone git@github.com:pymeadow/ccg2lambda_pipe.git
cd ccg2lambda_pipe/docker && docker-compose up
```
This will setup the whole environment in a docker container and runs the pipeline on the sentences 
which are stored in `sample_run/sentences.txt`. After a successfull run, you should be able to see
the output files such as `sample_run/sentences.pro.html` and `sample_run/sentences.sem.html`

## Installing locally

You need a setup like this:

* Ubuntu 18.04
* git version 2.17.1 
* Python 3.10.8
* pip 22.2.2

### 1.1 Prerequisites

```
sudo apt-get install libxml2-dev libxslt1-dev
sudo apt-get install python3.10-venv
sudo apt-get install zip unzip
```

### 1.2 Install CCG2Lambda

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

### 1.3 Install COQ

```
sudo apt-get install coq
coqc --version
The Coq Proof Assistant, version 8.6 (October 2017)
compiled on Oct 28 2017 14:23:55 with OCaml 4.05.0
```

`resources/coq_entail/coqlib.vo` was compiled by `cogc` and is ready to use by `coqtop`.


### 1.4 Install C&C Parser

```
./ccg2lamp/en/install_candc.sh
```

# 2 Validation Tests

## 2.1 Original Tests

```
python -m ccg2lamp.scripts.run_tests

----------------------------------------------------------------------
Ran 162 tests in 1.342s

OK (expected failures=3)

```

## 2.2 Pipeline Tests

Run the Scikit-Learn pipelines on the test corpora to reproduce the result files:

```
find . -name eval_*.bash -exec {} \;

# all the result files are updated
ls -lt datasets/corpus_fail
ls -lt datasets/corpus_test

# but no file has been changed
git status

```
