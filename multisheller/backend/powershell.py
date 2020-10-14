from multisheller import cmds
from .common import *
from .visitor import NodeVisitor
import re

def ensure_quotes(x):
    if x[0] == '"' or x[0] == '\'' and x[-1] == x[0]:
      return x
    else:
        # TODO powershell don't escape spaces etc
        return f"\"{x}\""

def wrap_try(x):
    return "try { " + x + "}\ncatch { Write-Host \"Failed to execute " + x + "\" }"

class PowerShellVisitor(NodeVisitor):
    def visit_BinOp(self, op):
        op_map = {
            # 'add': '+',
            'eq': '-eq',
            'lt': '-lt',
            'le': '-le',
            'gt': '-gt',
            'ge': '-ge',
            'ne': '-ne',
            'or': '-or',
            'and': '-and',
        }

        if op.op in ('export', 'assign'):
            if op.op == 'export':
                return f"$Env:{self.visit(op.lhs)}={self.visit(op.rhs)}"
            else:
                return f"{self.visit(op.lhs)}={self.visit(op.rhs)}"
        return f"({self.visit(op.lhs)}) {op_map[op.op]} ({self.visit(op.rhs)})"

    def visit_UnaryOp(self, node):
        op_map = {
            'not': '!'
        }
        if node.op in ('unset', 'is_set'):
            if type(node.value) is cmds.EnvNode:
                prefix = 'env:'
            elif type(node.value) is cmds.VarNode:
                prefix = 'variable:'
            else:
                raise RuntimeError("Can only unset Env and Var")

            if node.op == 'unset':
                return wrap_try(f"Remove-Item {prefix}{node.value.varname}")
            else:
                return f"Test-Path {prefix}{node.value.varname}"

        return f"{op_map[node.op]} {self.visit(node.value)}"

    def visit_StrOp(self, node):
        q = ensure_quotes
        if node.op == 'quoted':
            return q(node.value)
        elif node.op == 'starts_with':
            return f"{q(self.visit(node.lhs))} == {q(self.visit(node.rhs))}*"
        elif node.op == 'ends_with':
            return f"{q(self.visit(node.lhs))} == *{q(self.visit(node.rhs))}"
        elif node.op == 'contains':
            return f"{q(self.visit(node.lhs))} == *{q(self.visit(node.rhs))}*"

    def visit_Env(self, op):
        return f"$Env:{self.visit(op.varname)}"

    def visit_Var(self, op):
        return f"${self.visit(op.varname)}"

    def visit_Conditional(self, op):
        then_expr, else_expr = "", ""
        if op.then_expr:
            then_expr = "{\n    " + self.visit(op.then_expr) + "\n}\n"
        if op.else_expr:
            else_expr = "else {\n    " + self.visit(op.else_expr) + "\n}\n"

        return f"if ({self.visit(op.if_expr)}) {then_expr}{else_expr}\n"

    def visit_PathOp(self, node):
        q = ensure_quotes
        if node.op == 'join':
            return f"(Join-Path -Path {self.visit(node.lhs)} -ChildPath {self.visit(node.rhs)})"
        elif node.op == 'is_file':
            return f"Test-Path {self.visit(node.lhs)} -PathType Leaf"
        if node.op == 'is_dir':
            return f"Test-Path {self.visit(node.lhs)}"
        if node.op == 'path_remove':
            return "$Env:PATH = ($Env:PATH.Split(';') | Where-Object { $_ -ne '" + self.visit(node.lhs) + "' }) -join ';'"
        if node.op == 'path_append':
            return f"$Env:PATH+=\";{self.visit(node.lhs)}\""
        if node.op == 'path_prepend':
            return f"$Env:PATH=\"{self.visit(node.lhs)};$Env:PATH\""

    def visit_Call(self, node):
        args = ' '.join([self.visit(str_quote(arg)) for arg in node.args])
        return f"{node.cmd} {args}"


    def visit_default(self, node):
        return str(node)

def to_script(script):
    visitor = PowerShellVisitor()
    res = []
    for cmd in script.cmds:
        res.append(visitor.visit(cmd))

    return '\n'.join(res)