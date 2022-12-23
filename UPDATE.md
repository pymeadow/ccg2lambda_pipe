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

Run the installation test:

Set these environment variables to the folders you chose, so the program can find them:

```
export NLTK_DATA_PATH=~/nltk_data
export COQ_LIB_PATH=./coq_entail/coqlib.v
export COQPATH=$(dirname $COQ_LIB_PATH)

python3 scripts/run_tests.py
----------------------------------------------------------------------
Ran 162 tests in 1.167s

OK (expected failures=3)
```

Make necessary changes to the environment variables in `pipelines/pipeline.bash` if 
they are different from those described above.

Run the pipeline on the test corpus to reproduce the results in [README.md](./README.md):

```
pipelines/pipeline.bash datasets/corpus_test/sentences.txt
yes

git diff
```

`git diff` should not show any files under folder `datasets` are modified.
This indicates the program produced the same (and correct) results on your machine.

All done, congratulations!
