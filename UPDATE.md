# 1 Installation

* Ubuntu 18.04
* Python 3.10.8
* pip 22.2.2

## 1.1 Prerequisites

```
sudo apt-get install libxml2-dev libxslt1-dev
sudo apt-get install python3.10-venv
sudo apt-get install zip unzip
```

## 1.2 Install CCG2Lambda

```
git clone git@github.com:pymeadow/ccg2lambda_pipe.git

python3 -m venv ../../py_environs/ccg2lambda
source ../../py_environs/ccg2lambda/bin/activate

pip3 install -r requirements.txt

# download wordnet and punctuations for English tokenization
python3 -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt')"
cd ~/nltk_data/tokenizer
/usr/bin/unzip punkt.zip

python3 scripts/run_tests.py
----------------------------------------------------------------------
Ran 162 tests in 1.167s

OK (expected failures=3)
```

## 1.3 Install COQ

```
sudo apt-get install coq
coqc --version
The Coq Proof Assistant, version 8.6 (October 2017)
compiled on Oct 28 2017 14:23:55 with OCaml 4.05.0

# compile the tactics for textual entailment
coqc coqlib.v

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

Run the pipeline on the test corpus to reproduce the results in [README.md](./README.md):

```
pipelines/pipeline.bash datasets/corpus_test/sentences.txt
yes
```

Run the pipeline on 3 Stanford NLI sentence pairs:

```
pipelines/pipeline.bash datasets/corpus_snli/sentences_entail.txt
unknown
pipelines/pipeline.bash datasets/corpus_snli/sentences_neutral.txt
unknown
pipelines/pipeline.bash datasets/corpus_snli/sentences_contrad.txt
unknown
```

