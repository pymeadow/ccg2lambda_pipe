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

python3 -c "import nltk; nltk.download('wordnet')"
cd ~/nltk_data/corpora
/usr/bin/unzip wordnet.zip

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
```

## 1.4 Install C&C Parser
```
./en/install_candc.sh
Setting en/parser_location.txt pointing to .../ccg2lambda_pipe/candc-1.00
```

# 2 Validation Tests

## 2.1 Semantic Analysis

```
coqc coqlib.v

ls -alt
12146 coqlib.glob
21217 coqlib.vo
1316  .coqlib.vo.aux

cat datasets/corpus_test/sentences.txt | sed -f en/tokenizer.sed > datasets/corpus_test/sentences.tok
./candc-1.00/bin/candc --models candc-1.00/models --candc-printer xml --input datasets/corpus_test/sentences.tok > datasets/corpus_test/sentences.candc.xml

1 parsed at B=0.075, K=20
1 coverage 100%
1 stats 4.54329 232 296
2 parsed at B=0.075, K=20
2 coverage 100%
2 stats 3.61092 99 119
3 parsed at B=0.075, K=20
3 coverage 100%
3 stats 3.09104 93 110

python3 en/candc2transccg.py datasets/corpus_test/sentences.candc.xml > datasets/corpus_test/sentences.xml

python3 scripts/semparse.py datasets/corpus_test/sentences.xml en/semantic_templates_en_emnlp2015.yaml datasets/corpus_test/sentences.sem.xml
```

## 2.2 Textual Entailment

```
python3 scripts/prove.py datasets/corpus_test/sentences.sem.xml --graph_out datasets/corpus_test/graphdebug.html

```

## 2.3 Parse Tree Visualization

```
python3 scripts/visualize.py datasets/corpus_test/sentences.xml > datasets/corpus_test/sentences.html
```