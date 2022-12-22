#!/bin/bash

INPUT_PATH=$1
set -x

input_dir=$(dirname $INPUT_PATH)
input_file=$(basename $INPUT_PATH .txt)

token_file=$input_dir/$input_file.tok.txt
cat $INPUT_PATH | python3 en/tokenizer.py > $token_file

candc_xml=$input_dir/$input_file.candc.xml
./candc-1.00/bin/candc --models candc-1.00/models --candc-printer xml --input $token_file > $candc_xml

parse_xml=$input_dir/$input_file.syn.xml
en/candc2transccg.py $candc_xml > $parse_xml

sem_xml=$input_dir/$input_file.sem.xml
scripts/semparse.py $parse_xml en/semantic_templates_en_emnlp2015.yaml $sem_xml

entail_html=$input_dir/${input_file}.pro.html
proof_xml=$input_dir/${input_file}.pro.xml
scripts/prove.py $sem_xml --proof $proof_xml --graph_out $entail_html

tree_html=$input_dir/${input_file}.syn.html
scripts/visualize.py $parse_xml > $tree_html

set +x