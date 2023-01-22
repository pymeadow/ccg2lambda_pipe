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
import os
import sys
import textwrap
import traceback

from nltk.sem.logic import LogicalExpressionException

from .ccg2lambda_tools import assign_semantics_to_ccg
from .semantic_index import SemanticIndex

from .xml_utils import serialize_tree_to_file, deserialize_file_to_tree

SEMANTIC_INDEX=None
ARGS=None
SENTENCES=None
kMaxTasksPerChild=None

my_logger = logging.getLogger(__name__)

def sem_parse(root):
    """extend sentence nodes with semantic nodes"""
    global SENTENCES, SEMANTIC_INDEX

    SEMANTIC_INDEX = SemanticIndex(ARGS.templates)
    SENTENCES = root.findall('.//sentence')
    # print('Found {0} sentences'.format(len(SENTENCES)))
    # from pudb import set_trace; set_trace()
    sentence_inds = range(len(SENTENCES))
    sem_nodes_lists = semantic_parse_sentences(sentence_inds, ARGS.ncores)
    assert len(sem_nodes_lists) == len(SENTENCES), \
        'Element mismatch: {0} vs {1}'.format(len(sem_nodes_lists), len(SENTENCES))
    my_logger.info('Adding XML semantic nodes to sentences...')
    for sentence, sem_nodes in zip(SENTENCES, sem_nodes_lists):
        sentence.extend(sem_nodes)
    
def main(args = None):
    global ARGS
    DESCRIPTION=textwrap.dedent("""\
            categories_template.yaml should contain the semantic templates
              in YAML format.
            parsed_sentence.xml contains the CCG-parsed sentences.
            If --arbi-types is specified, then the arbitrary specification of
              types is enabled, thus using the argument as the field of the semantic
              template that is used. E.g, by specifying "--arbi-types coq_type"
              and a semantic template:
            - semantics: \P x.P(x)
              category: NP
              coq_type: Animal
            The type "Animal" will be used for this expression. Otherwise,
            types of the sem/logic module of NLTK are used.
      """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION)
    parser.add_argument("ccg")
    parser.add_argument("templates")
    parser.add_argument("sem")
    parser.add_argument("--arbi-types", action="store_true", default=False)
    parser.add_argument("--gold_trees", action="store_true", default=True)
    parser.add_argument("--nbest", nargs='?', type=int, default="0")
    parser.add_argument("--ncores", nargs='?', type=int, default="3",
        help="Number of cores for multiprocessing.")
    ARGS = parser.parse_args()
      
    if not os.path.exists(ARGS.templates):
        print('File does not exist: {0}'.format(ARGS.templates))
        sys.exit(1)
    if not os.path.exists(ARGS.ccg):
        print('File does not exist: {0}'.format(ARGS.ccg))
        sys.exit(1)
    
    logging.basicConfig(level=logging.WARNING)

    root = deserialize_file_to_tree(ARGS.ccg)

    sem_parse(root)        
    my_logger.info('Finished adding XML semantic nodes to sentences.')

    serialize_tree_to_file(root, ARGS.sem)

def semantic_parse_sentences(sentence_inds, ncores=1):
    if ncores <= 1:
        sem_nodes_lists = semantic_parse_sentences_seq(sentence_inds)
    else:
        sem_nodes_lists = semantic_parse_sentences_par(sentence_inds, ncores)
    sem_nodes_lists = [
        [etree.fromstring(s) for s in sem_nodes] for sem_nodes in sem_nodes_lists]
    return sem_nodes_lists

def semantic_parse_sentences_par(sentence_inds, ncores=3):
    pool = Pool(processes=ncores, maxtasksperchild=kMaxTasksPerChild)
    sem_nodes = pool.map(semantic_parse_sentence, sentence_inds)
    pool.close()
    pool.join()
    return sem_nodes

def semantic_parse_sentences_seq(sentence_inds):
    sem_nodes = []
    for sentence_ind in sentence_inds:
        sem_node = semantic_parse_sentence(sentence_ind)
        sem_nodes.append(sem_node)
    return sem_nodes

def semantic_parse_sentence(sentence_ind):
    """
    `sentence` is an lxml tree with tokens and ccg nodes.
    It returns an lxml semantics node.
    """
    sentence = SENTENCES[sentence_ind]
    sem_nodes = []
    # TODO: try to prevent semantic parsing for fragmented CCG trees.
    # Otherwise, produce fragmented semantics.
    if ARGS.gold_trees:
        # In xpath, elements are 1-indexed.
        # However, gold_tree annotations assumed zero-index.
        # This line fixes it.
        tree_indices = [int(sentence.get('gold_tree', '0')) + 1]
    if ARGS.nbest != 1:
        tree_indices = get_tree_indices(sentence, ARGS.nbest)
    for tree_index in tree_indices: 
        sem_node = etree.Element('semantics')        
        ccg_tree = sentence.xpath(f'./ccg[{tree_index}]/@id')[0]
        ccg_root = sentence.xpath(f'./ccg[{tree_index}]/@root')[0]

        try:
            sem_tree = assign_semantics_to_ccg(
                sentence, SEMANTIC_INDEX, tree_index)
            filter_attributes(sem_tree)
            sem_node.extend(sem_tree.xpath('.//descendant-or-self::span'))
            sem_node.set('status', 'success')
        except Exception as e:
            # add a special child span node with EMPTY formula
            empty_span = etree.Element("span")
            empty_span.set("id", f"s{sentence_ind}_sp0")
            empty_span.set("sem", "EMPTY")
            sem_node.append(empty_span)
            sem_node.set('status', 'failed')

            sentence_surf = ' '.join(sentence.xpath('tokens/token/@surf'))
            my_logger.debug(f'Semantic parse failed with: {e}\nSentence: {sentence_surf}\n')
            print(traceback.print_exc())

        sem_node.set('ccg_id', ccg_tree)
        sem_node.set('root', ccg_root)
        sem_nodes.append(sem_node)
    return [etree.tostring(sem_node) for sem_node in sem_nodes]

def get_tree_indices(sentence, nbest):
    num_ccg_trees = int(sentence.xpath('count(./ccg)'))
    if nbest < 1:
        nbest = num_ccg_trees
    return list(range(1, min(nbest, num_ccg_trees) + 1))

keep_attributes = set(['id', 'child', 'sem', 'type'])
def filter_attributes(tree):
    if 'coq_type' in tree.attrib and 'child' not in tree.attrib:
        sem_type = \
            tree.attrib['coq_type'].lstrip('["Parameter ').rstrip('."]')
        if sem_type:
            tree.attrib['type'] = sem_type
    attrib_to_delete = [a for a in tree.attrib.keys() if a not in keep_attributes]
    for a in attrib_to_delete:
        del tree.attrib[a]
    for child in tree:
        filter_attributes(child)
    return

if __name__ == '__main__':
    main()
