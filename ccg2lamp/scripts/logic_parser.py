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
import logging
#import traceback

from nltk.sem.logic import Expression
from nltk.sem.logic import LogicParser
from nltk.sem.logic import LogicalExpressionException

my_logger = logging.getLogger(__name__)

class InvalidExpression(Expression):
    def __init__(self, exp: Expression):
        self.exp_list = [exp]
    
    def simplify(self):
        return self

    def visit(self, function, combinator):
        return self

    def __add__(self, exp: Expression):
        self.exp_list += exp
        return self
    
    def __str__(self):
        return ";".join(map(str, self.exp_list))

logic_parser = LogicParser(type_check=False)
def lexpr(formula_str):
    try:
        expr = logic_parser.parse(formula_str)
        return expr
    except LogicalExpressionException as e:
        my_logger.error('Failed to parse {0}. Error: {1}'.format(formula_str, e))
        #print(traceback.print_stack())
        return None
