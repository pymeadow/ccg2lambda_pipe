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

PE_PRE = "PE:"
PE_DEL = "|"

class PartialExpression(Expression):
    """Store fragments of valid expressions that cannot be composed"""
    def __init__(self, exp_list):
        # exp_list: List[Expression]
        self.exp_list = exp_list
    
    def applyto(self, other):
        # support function application: self(other)
        # called by: parent.__call__(other)
        return self + other

    def constants(self):
        return []
    
    def equiv(self, other):
        return all(self.exp_list == other.exp_list)

    def findtype(self, *args):
        return None

    def free(self):
        return []

    def negate(self):
        return self

    def normalize(self, *args):
        return self

    def predicates(self):
        return []
    
    def replace(self, *args):
        return self

    def simplify(self):
        return self

    def substitute_bindings(self, *args):
        return self

    def typecheck(self, *args):
        return {}

    def variables(self):
        return []

    def visit(self, *args):
        return self

    def __add__(self, other):
        assert isinstance(other, Expression)
        if isinstance(other, PartialExpression):
            self.exp_list += other.exp_list
        else:
            self.exp_list.append(other)
        return self

    def __str__(self):
        return PE_PRE + PE_DEL.join(map(str, self.exp_list))

def is_partial_expression(formula_str):
    return formula_str[: len(PE_PRE)] == PE_PRE

def combine_partial_expressions(function: Expression, argument: Expression):
    # combine function with argument if one of them is PartialExpression
    if isinstance(function, PartialExpression):
        function += argument
        return function
    if isinstance(argument, PartialExpression):
        argument += function
        return argument
    return None

def recover_partial_expressions(evaluation, function, argument):
    # check if evaluation is valid
    if lexpr(str(evaluation)):
        # the expression is valid as it can be parsed
        return evaluation
    else:
        # the expression is invalid, recover its parts
        evaluation = PartialExpression([function, argument])
        return evaluation

logic_parser = LogicParser(type_check=False)
def lexpr(formula_str):
    if is_partial_expression(formula_str):
        pe_body = formula_str[len(PE_PRE):]
        return PartialExpression(pe_body.split(PE_DEL))

    try:
        expr = logic_parser.parse(formula_str)
        return expr
    except LogicalExpressionException as e:
        my_logger.debug(f'Failed to parse {formula_str}. Error: {e}')
        #print(traceback.print_stack())
        return None
