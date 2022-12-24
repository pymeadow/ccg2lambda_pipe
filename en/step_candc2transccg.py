import logging
from typing import Tuple

import lxml

from sklearn.base import TransformerMixin

from en.candc2transccg import translate_candc_tree

my_logger = logging.getLogger(__name__)

class CNC2CCGTranslator(TransformerMixin):
    """Adapt en/candc2transccg.py to scikit-learn transformer"""
    def __init__(self):
        pass
    
    def transform(self, X: Tuple[str, str|None]|None) -> Tuple[lxml.etree._Element, str]|None:
        if X is None: return None
        xml_fname, log_fname = X
        transccg_xml_tree, encoding = translate_candc_tree(xml_fname, log_fname)
        return transccg_xml_tree, encoding

# unit test
if __name__ == "__main__":
    from pipelines.step_tree_io import CCGTreeWriter

    trans = CNC2CCGTranslator()
    tree, encoding = trans.transform(("datasets/corpus_test/sentences.candc.xml", None))
    print(tree, encoding)
    assert type(tree) is lxml.etree._Element

    writer = CCGTreeWriter(output_file="datasets/corpus_test/sentences.syn.xml")
    tree, encoding = writer.transform((tree, encoding))
    print(tree, encoding)
    assert type(tree) is lxml.etree._Element
    