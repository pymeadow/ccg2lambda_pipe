import codecs

from lxml import etree

from ccg2lamp.scripts.utils import time_count

def deserialize_file_to_tree(xml_fname):
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.parse(xml_fname, parser)
    
def serialize_tree(tree, encoding='utf-8'):
    tree_str = etree.tostring(
        tree, xml_declaration=True, encoding=encoding, pretty_print=True)
    return tree_str

@time_count
def serialize_tree_to_file(tree_xml, fname, encoding='utf-8'):
    root_xml_str = serialize_tree(tree_xml, encoding)
    with codecs.open(fname, 'wb') as fout:
        fout.write(root_xml_str + b"\n")
    return

