from .visitor import NodeVisitor
from .common import *

import re

def ensure_quotes(x):
    if x[0] == '"' or x[0] == '\'' and x[-1] == x[0]:
      return x
    else:
      return f"\"{re.escape(x)}\""


class BashVisitor(NodeVisitor):
    def visit_BinOp(self, op):
        op_map = {
            'add': '+',
            'eq': '==',
            'lt': '<',
            'le': '<=',
            'gt': '>',
            'ge': '>=',
            'ne': '!=',
            'or': 'or',
            'and': 'and',
        }

        if op.op in ('export', 'assign'):
            if op.op == 'export':
                return f"${self.visit(op.lhs)}={self.visit(op.rhs)}"
            else:
                return f"{self.visit(op.lhs)}={self.visit(op.rhs)}"
        return f"{self.visit(op.lhs)} {op_map[op.op]} {self.visit(op.rhs)}"

    def visit_UnaryOp(self, op):
        op_map = {
            'not': 'not'
        }
        if op.op == 'is_set':
            return ensure_quotes(op.value.varname) + " in ${...}"
        if op.op == 'unset':
            return f"del ${ensure_quotes(op.value.varname)}"
        return f"{op_map[op.op]} {self.visit(op.value)}"

    def visit_StrOp(self, node):
        q = ensure_quotes
        if node.op == 'quoted':
            return q(node.value)
        elif node.op == 'starts_with':
            return f"{q(self.visit(node.lhs))}.startswith({q(self.visit(node.rhs))})"
        elif node.op == 'ends_with':
            return f"{q(self.visit(node.lhs))}.endswith({q(self.visit(node.rhs))})"
        elif node.op == 'contains':
            return f"({q(self.visit(node.rhs))} in {q(self.visit(node.lhs))})"

    def visit_Env(self, op):
        return f"${self.visit(op.varname)}"

    def visit_Conditional(self, op):
        then_expr, else_expr = "", ""
        if op.then_expr:
            then_expr = f"\n{join_expr(op.then_expr, self.visit)}"
        if op.else_expr:
            else_expr = f"\nelse:\n{join_expr(op.else_expr, self.visit)}"

        return f"if ({self.visit(op.if_expr)}):{then_expr}{else_expr}\n"

    def visit_Call(self, node):
        args = ' '.join([self.visit(str_quote(arg)) for arg in node.args])
        return f"{node.cmd} {args}"

    def visit_PathOp(self, node):
        q = ensure_quotes
        if node.op == 'join':
            return f"@(os.path.join({q(self.visit(node.lhs))}, {q(self.visit(node.rhs))}))"
        elif node.op == 'is_file':
            return f"os.path.isfile({q(self.visit(node.lhs))})"
        if node.op == 'is_dir':
            return f"os.path.isdir({q(self.visit(node.lhs))})"
        if node.op == 'path_remove':
            rm_path = q(self.visit(node.lhs))
            return f"while({rm_path} in $PATH): $PATH.remove({rm_path})"
        if node.op == 'path_append':
            return f"$PATH.append({q(self.visit(node.lhs))})"
        if node.op == 'path_prepend':
            return f"$PATH.insert(0, {q(self.visit(node.lhs))})"

    def visit_ListOp(self, node):
        q = ensure_quotes
        if node.op == 'list_remove':
            return f"listremove({q(self.visit(node.rhs))}, {q(self.visit(node.lhs))})"
        if node.op == 'list_append':
            return f"listappend({q(self.visit(node.rhs))}, {q(self.visit(node.lhs))})"
        if node.op == 'list_prepend':
            return f"listprepend({q(self.visit(node.rhs))}, {q(self.visit(node.lhs))})"

    def visit_default(self, node):
        return str(node)


xonsh_imports = """
import os, sys
"""

def to_script(script):

    res = []
    visitor = BashVisitor()

    xonsh_path_functions = """
# Inspired from http://www.linuxfromscratch.org/blfs/view/svn/postlfs/profile.html
# and ported to xonsh.
# Functions to help us manage paths.  Second argument is the name of the
# list variable to be modified
def listremove(elemToRemove, varToModify):
    # xonsh has diffent types for the variables depending on their name,
    # see https://xon.sh/tutorial.html#environment-types
    # so we need to always distinguish three cases:
    # * the variable does not exist
    # * the variable is a string
    # * the variable is a list
    if (varToModify not in ${...}):
        return
    elif (type(${varToModify}) == str):
        ${varToModify} = os.pathsep.join(list(filter(lambda el: el != elemToRemove, ${varToModify}.split(os.pathsep))))
    elif (type(${varToModify}) == type($PATH)):
        while(elemToRemove in ${varToModify}): ${varToModify}.remove(elemToRemove)

def listprepend(elemToPrepend, varToModify):
    if (varToModify not in ${...}):
        ${varToModify}=elemToPrepend
    elif (type(${varToModify}) == str):
        ${varToModify} = os.pathsep.join([elemToPrepend] + ${varToModify}.split(os.pathsep))
    elif (type(${varToModify}) == type($PATH)):
        ${varToModify}.insert(0, elemToPrepend)

def listappend(elemToAppend, varToModify):
    if (varToModify not in ${...}):
        ${varToModify}=elemToAppend
    elif (type(${varToModify}) == str):
        ${varToModify} = os.pathsep.join(${varToModify}.split(os.pathsep) + [elemToAppend])
    elif (type(${varToModify}) == type($PATH)):
        ${varToModify}.append(elemToAppend)

"""

    for cmd in script.cmds:
        res.append(visitor.visit(cmd))

    return xonsh_imports + xonsh_path_functions + '\n'.join(res)