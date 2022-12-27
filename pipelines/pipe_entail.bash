#!/bin/bash

INPUT_PATH=$1

if [ -z "$INPUT_PATH" ]; then
	echo "Usage: $0 INPUT_PATH"
	exit
fi

set -x

# change these variables if necessary to point to the correct folders
export COQ_LIB_PATH=./coq_entail/coqlib.v
export COQPATH=$(dirname $COQ_LIB_PATH)
export NLTK_DATA_PATH=~/nltk_data
export PYTHONPATH=.:scripts

input_dir=$(dirname $INPUT_PATH)
input_file=$(basename $INPUT_PATH .txt)

token_file=$input_dir/$input_file.tok.txt
cat $INPUT_PATH | python3 en/tokenizer.py > $token_file

candc_xml=$input_dir/$input_file.candc.xml
./candc-1.00/bin/candc --models candc-1.00/models --candc-printer xml --input $token_file > $candc_xml

parse_xml=$input_dir/$input_file.syn.xml
en/candc2transccg.py $candc_xml > $parse_xml

parse_html=$input_dir/${input_file}.syn.html
scripts/visualize.py $parse_xml > $parse_html

sem_xml=$input_dir/$input_file.sem.xml
scripts/semparse.py $parse_xml en/semantic_templates_en_emnlp2015.yaml $sem_xml

sem_html=$input_dir/${input_file}.sem.html
scripts/visualize.py $sem_xml > $sem_html

entail_html=$input_dir/${input_file}.pro.html
proof_xml=$input_dir/${input_file}.pro.xml
scripts/prove.py $sem_xml --proof $proof_xml --graph_out $entail_html

set +x