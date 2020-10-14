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

    def visit_default(self, node):
        return str(node)


xonsh_imports = """
import os, sys
"""

def to_script(script):

    res = []
    visitor = BashVisitor()

    for cmd in script.cmds:
        res.append(visitor.visit(cmd))

    return xonsh_imports + '\n'.join(res)