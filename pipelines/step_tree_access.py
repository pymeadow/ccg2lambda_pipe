from typing import List, Dict

from lxml import etree
from scripts.theorem import generate_semantics_from_doc
from scripts.semantic_types import get_dynamic_library_from_doc

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
        
