#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2015 Pascual Martinez-Gomez
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import print_function

import argparse
import codecs
import logging
from lxml import etree
from multiprocessing import Pool
from multiprocessing import Lock
import os
from subprocess import TimeoutExpired
import sys
import textwrap
import traceback

from .semantic_tools import prove_doc
from .utils import time_count
from .visualization_tools import convert_root_to_mathml

from .xml_utils import serialize_tree_to_file, deserialize_file_to_tree

ARGS=None
DOCS=None
ABDUCTION=None
kMaxTasksPerChild=None
lock = Lock()

my_logger = logging.getLogger(__name__)

def main(args = None):
    global ARGS
    DESCRIPTION=textwrap.dedent("""\
            The input file sem should contain the parsed sentences. All CCG trees correspond
            to the premises, except the last one, which is the hypothesis.
      """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION)
    parser.add_argument("sem", help="XML input filename with semantics")
    parser.add_argument("--proof", default="",
        help="XML output filename with proof information")
    parser.add_argument("--graph_out", nargs='?', type=str, default="",
        help="HTML graphical output filename.")
    parser.add_argument("--abduction", nargs='?', type=str, default="no",
        choices=["no", "naive", "spsa"],
        help="Activate on-demand axiom injection (default: no axiom injection).")
    parser.add_argument("--gold_trees", action="store_true", default=True)
    parser.add_argument("--print", nargs='?', type=str, default="result",
        choices=["result", "status"],
        help="Print to standard output the inference result or termination status.")
    parser.add_argument("--print_length", nargs='?', type=str, default="full",
        choices=["full", "short", "zero"],
        help="Length of printed output.")
    parser.add_argument("--timeout", nargs='?', type=int, default="100",
        help="Maximum running time for each possible theorem.")
    parser.add_argument("--ncores", nargs='?', type=int, default="1",
        help="Number of cores for multiprocessing.")
    ARGS = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
      
    if not os.path.exists(ARGS.sem):
        my_logger.debug('File does not exist: {0}'.format(ARGS.sem))
        parser.print_help(file=sys.stderr)
        sys.exit(1)
    
    root = deserialize_file_to_tree(ARGS.sem)
    prove_entail(root)

    if ARGS.proof:
        serialize_tree_to_file(root, ARGS.proof)

    if ARGS.graph_out:
        html_str = convert_root_to_mathml(root, ARGS.gold_trees)
        with codecs.open(ARGS.graph_out, 'w', 'utf-8') as fout:
            fout.write(html_str + "\n")

def prove_entail(root):
    """new entry function that accepts a XML tree"""
    global DOCS
    global ABDUCTION

    if ARGS.abduction == "spsa":
        from .abduction_spsa import AxiomsWordnet
        ABDUCTION = AxiomsWordnet()
    elif ARGS.abduction == "naive":
        from .abduction_naive import AxiomsWordnet
        ABDUCTION = AxiomsWordnet()

    DOCS = root.findall('.//document')
    document_inds = range(len(DOCS))
    proof_nodes = prove_docs(document_inds, ARGS.ncores)
    assert len(proof_nodes) == len(DOCS), \
        'Num. elements mismatch: {0} vs {1}'.format(len(proof_nodes), len(DOCS))
    for doc, proof_node in zip(DOCS, proof_nodes):
        doc.append(proof_node)
    
@time_count
def prove_docs(document_inds, ncores=1):
    if ncores <= 1:
        proof_nodes = prove_docs_seq(document_inds)
    else:
        proof_nodes = prove_docs_par(document_inds, ncores)
    proof_nodes = [etree.fromstring(p) for p in proof_nodes]
    return proof_nodes

def prove_docs_par(document_inds, ncores=3):
    pool = Pool(processes=ncores, maxtasksperchild=kMaxTasksPerChild)
    proof_nodes = pool.map(prove_doc_ind, document_inds)
    pool.close()
    pool.join()
    return proof_nodes

def prove_docs_seq(document_inds):
    proof_nodes = []
    for document_ind in document_inds:
        proof_node = prove_doc_ind(document_ind)
        proof_nodes.append(proof_node)
    return proof_nodes

def prove_doc_ind(document_ind):
    """
    Perform RTE inference for the document ID document_ind.
    It returns an XML node with proof information.
    """
    global lock
    doc = DOCS[document_ind]
    proof_node = etree.Element('proof')
    inference_result = 'unknown'
    try:
        theorem = prove_doc(doc, ABDUCTION, ARGS)
        proof_node.set('status', 'success')
        inference_result = theorem.result
        proof_node.set('inference_result', inference_result)
        theorems_node = theorem.to_xml()
        proof_node.append(theorems_node)
    except TimeoutExpired as e:
        proof_node.set('status', 'timedout')
        proof_node.set('inference_result', 'unknown')
    except Exception as e:
        doc_id = doc.get('id', '(unspecified)')
        lock.acquire()
        
        # get the source of exception
        _exc_type, _exc_obj, tb = sys.exc_info()
        line_no = tb.tb_lineno
        file_name = tb.tb_frame.f_code.co_filename
        xml_text = etree.tostring(doc, encoding='utf-8', pretty_print=True).decode('utf-8')
        logging.error(f'Exception "{e}" from {file_name}:{line_no} for {doc_id}')
        print(traceback.print_exc())

        lock.release()
        proof_node.set('status', 'failed')
        proof_node.set('inference_result', 'unknown')
    if ARGS.print == 'status':
        label = proof_node.get('status')
    else:
        label = proof_node.get('inference_result', 'unknown')
    lock.acquire()
    if ARGS.print_length == 'full':
        pair_id = doc.get('pair_id', '').strip()
        result = '{0} {1}'.format(pair_id, label) if len(pair_id) > 0 else label
        my_logger.debug(result)
    elif ARGS.print_length == 'short':
        my_logger.debug(label[0])
    lock.release()
    sys.stdout.flush()
    return etree.tostring(proof_node)

if __name__ == '__main__':
    main()
