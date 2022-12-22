import os
import subprocess
import logging
import shlex

from sklearn.base import TransformerMixin

my_logger = logging.getLogger(__name__)

class CCGSemantics(TransformerMixin):
