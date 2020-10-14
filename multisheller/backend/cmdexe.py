from .visitor import NodeVisitor
import re

def ensure_quotes(x):
    if x[0] == '"' or x[0] == '\'' and x[-1] == x[0]:
      return x
    else:
      return f"\"{re.escape(x)}\""


class CmdExeVisitor(NodeVisitor):
    def visit_BinOp(self, node):
        op_map = {
            # 'add': '+',
            'eq': 'EQU',
            'lt': 'LSS',
            'le': 'LEQ',
            'gt': 'GTR',
            'ge': 'GEQ',
            'ne': 'NEQ'
            # 'or': '||',
            # 'and': '&&',
        }

        if node.op in ('export', 'assign'):
            if node.op == 'export':
                return f"set {self.visit(node.lhs)}={self.visit(node.rhs)}"
            else:
                return f"{self.visit(node.lhs)}={self.visit(node.rhs)}"
        return f"{self.visit(node.lhs)} {op_map[node.op]} {self.visit(node.rhs)}"

    def visit_UnaryOp(self, node):
        op_map = {
            'not': 'NOT'
        }
        if node.op == 'is_set':
            return f"{ensure_quotes(self.visit(node.value))} NEQ \"\""
        if node.op == 'unset':
            return f"set {node.value.varname}="
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
        return f"%{self.visit(op.varname)}%"

    def visit_Conditional(self, op):
        then_expr, else_expr = "", ""
        if op.then_expr:
            then_expr = f"(\n    {self.visit(op.then_expr)}\n)"
        if op.else_expr:
            else_expr = f" else (\n    {self.visit(op.else_expr)}\n)"

        return f"if {self.visit(op.if_expr)} {then_expr}{else_expr}\n"

    def visit_Call(self, op):
        if op.cmd == 'echo':
            # return f"{op.cmd} {ensure_quotes(' '.join(op.args))}"
            pass
        return f"{op.cmd} {' '.join([self.visit(arg) for arg in op.args])}"

    def visit_default(self, node):
        return str(node)

def to_script(script):
    res = ['@echo off']
    visitor = CmdExeVisitor()

    for cmd in script.cmds:
        res.append(visitor.visit(cmd))

    return '\n'.join(res)