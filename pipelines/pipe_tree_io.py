"""Steps and utilities to read/write information from/to CCG trees"""
import os
import logging
from typing import List, Dict

from sklearn.base import TransformerMixin

from lxml import etree

from scripts.prove import serialize_tree_to_file
from scripts.theorem import generate_semantics_from_doc
from scripts.semantic_types import get_dynamic_library_from_doc

my_logger = logging.getLogger(__name__)

#===================================================
# Basic tree IO steps
#===================================================

class CCGTreeReader(TransformerMixin):
    """load CCG tree from file into memory"""
    def __init__(self):
        self.xml_parser = etree.XMLParser(remove_blank_text=True)
    
    def transform(self, input_file: str) -> etree._Element:
        assert os.path.exists(input_file)
        root = etree.parse(input_file, self.xml_parser)    
        return root

class CCGTreeWriter(TransformerMixin):
    """save CCG tree in memory to output file"""
    def __init__(self):
        """initialization"""
        self.output_file = None
    
    def set_params(self, output_file=None):
        """set the output file before transform"""
        assert output_file
        self.output_file = output_file       

    def transform(self, root: etree._Element) -> str:
        """save xml tree to file"""
        assert self.output_file
        serialize_tree_to_file(root, self.output_file)
        return self.output_file

#===================================================
# Tree utilities to support custom steps
#===================================================

class CCGTree():
    def __init__(self, root: etree._Element,
                 use_gold_trees: bool = False,
                 max_sentences: int = 100,
                 min_sentences: int = 1):
        self.ccg_tree = root
        self.max_sentences = max_sentences
        self.min_sentences = min_sentences
        self.use_gold_trees = use_gold_trees
    
    def get_doc_semantics(self, doc_element: etree._Element) -> List[Dict]:
        doc_semantics = []
        # sem_product = [semantics(s1) x ... x semantics(sn)]
        # where semantics(si) = [<semantics>{1, n_best}] for sentence si
        sem_product = generate_semantics_from_doc(doc_element, 
                                                max_gen=self.max_sentences, 
                                                use_gold_trees=self.use_gold_trees, 
                                                min_sentences=self.min_sentences)
        for sent_semantics in sem_product:
            dynamic_library_str, sent_formulas = get_dynamic_library_from_doc(doc_element, 
                                                                              sent_semantics)
            result = dict(dynamic_library=dynamic_library_str,
                          semantic_nodes=sent_semantics,
                          logic_formulas=sent_formulas)
            doc_semantics.append(result)
        return doc_semantics
        
    def get_semantics(self) -> List[Dict]:
        doc_elements = self.ccg_tree.findall('.//document')
        corpus_semantics = []
        for doc_node in doc_elements:
            doc_sem = self.get_doc_semantics(doc_node)
            result = dict(doc_node=doc_node, doc_sem=doc_sem)
            corpus_semantics.append(result)
        return corpus_semantics
        
#===================================================
# unit test
#===================================================
if __name__ == "__main__":
    from sklearn.pipeline import Pipeline
    tree_reader = CCGTreeReader()
    tree_writer = CCGTreeWriter()
    io_pipe = Pipeline([
        ("reader", tree_reader),
        ("writer", tree_writer)])
    # load xml file into memory then save it back to the same file
    # the file should not change
    input_file = "datasets/corpus_test/sentences.pro.xml"
    io_pipe.set_params(writer__output_file=input_file)
    output_file = io_pipe.transform(input_file)
    print(output_file)