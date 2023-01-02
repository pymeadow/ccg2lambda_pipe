from typing import List
from dataclasses import dataclass
from lxml import etree

@dataclass
class ParseData():
    parse_result: etree._Element = None
    parse_encode: str = 'utf-8'   
    parse_error: Exception = None
    input_file: str = None
    output_file: str = None
    
@ dataclass
class EntailProof():
    # represents an entailment inference over the document
    # <document>
    #    <proof status=, inference_result=>
    #       <master_theorem>...</master_theorem>
    #    </proof>
    # </document>
    status: str = "success" # success, timedout, failed
    inference_result: str = "unknown" # yes, no, unknown
    proof_node: etree._Element = None

@dataclass
class CorpusSemantics():
    # this represents one interpretation of a corpus
    # each sentence has n-best <semantics> elements
    # each <semantics> node contains a root logic formula
    # dynamic_library contains the semantic context
    # i.e. semantic entities and relations for the
    # entire corpus
    
    # common entities/relations of the corpus
    dynamic_library: str
    # one semantic node per sentence
    semantic_nodes: List[etree._Element]
    # one logic formula per sentence
    logic_formulas: List[object]

@dataclass
class DocumentSemantics():
    # a document contains a corpus: a collection of sentences
    # a corpus can have many interpretations
    doc_node: etree._Element
    doc_sem: List[CorpusSemantics]
    # common inference over the corpus
    doc_infer: EntailProof = None
    