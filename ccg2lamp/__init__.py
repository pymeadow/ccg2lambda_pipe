# figure out the global resource paths relevant to this file
import os

CCG2LAMP_HOME = os.path.dirname(os.path.dirname(__file__))

CCG2LAMP_PARSER_EXE = os.path.join(CCG2LAMP_HOME, "candc-1.00/bin/candc")
CCG2LAMP_PARSER_MODEL = os.path.join(CCG2LAMP_HOME, "candc-1.00/models")

CCG2LAMP_SEM_TEMPLATE = os.path.join(CCG2LAMP_HOME, "ccg2lamp/en/semantic_templates_en_emnlp2015.yaml")

CCG2LAMP_RESOURCES = os.path.join(CCG2LAMP_HOME, "resources")
CCG2LAMP_COQ_LIB = os.path.join(CCG2LAMP_RESOURCES, "coq_entail/coqlib.v")
CCG2LAMP_REPLACEMENT_FILE = os.path.join(CCG2LAMP_RESOURCES, "replacement.txt")

# set the environment variable for coqtop process
os.environ["COQPATH"] = os.path.dirname(CCG2LAMP_COQ_LIB)
