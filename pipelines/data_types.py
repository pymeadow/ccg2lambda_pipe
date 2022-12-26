
from dataclasses import dataclass
from lxml import etree

@dataclass
class ParseData():
    parse_result: etree._Element = None
    parse_encode: str = 'utf-8'   
    parse_error: Exception = None
    input_file: str = None
    output_file: str = None
    
