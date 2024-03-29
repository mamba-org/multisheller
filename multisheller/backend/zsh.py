from .common import join_expr
from .visitor import NodeVisitor
import re

def ensure_quotes(x):
    if x[0] == '"' or x[0] == '\'' and x[-1] == x[0]:
      return x
    else:
      return f"\"{x}\""


class BashVisitor(NodeVisitor):
    def visit_BinOp(self, op):
        op_map = {
            'add': '+',
            'eq': '-eq',
            'lt': '-lt',
            'le': '-le',
            'gt': '-gt',
            'ge': '-ge',
            'ne': '-ne',
            'or': '||',
            'and': '&&',
        }

        if op.op in ('export', 'assign'):
            if op.op == 'export':
                return f"export {self.visit(op.lhs)}={self.visit(op.rhs)}"
            else:
                return f"{self.visit(op.lhs)}={self.visit(op.rhs)}"
        return f"{self.visit(op.lhs)} {op_map[op.op]} {self.visit(op.rhs)}"

    def visit_UnaryOp(self, op):
        op_map = {
            'is_set': '! -z',
            'not': '!',
            'unset': 'unset'
        }
        return f"{op_map[op.op]} {self.visit(op.value)}"

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
        return f"${self.visit(op.varname)}"

    def visit_Conditional(self, op):
        then_expr, else_expr = "", ""
        if op.then_expr:
            then_expr = f"\nthen\n{join_expr(op.then_expr, self.visit)}"
        if op.else_expr:
            else_expr = f"\nelse\n{join_expr(op.else_expr, self.visit)}"

        return f"if [[ {self.visit(op.if_expr)} ]];{then_expr}{else_expr}\nfi;"

    def visit_Call(self, node):
        return f"{node.cmd} {' '.join([self.visit(arg) for arg in node.args])}"

    def visit_PathOp(self, node):
        if node.op == 'join':
            return f"{self.visit(node.lhs)}/{self.visit(node.rhs)}"
        elif node.op == 'is_file':
            return f"-f {self.visit(node.lhs)}"
        if node.op == 'is_dir':
            return f"-d {self.visit(node.lhs)}"
        if node.op == 'path_remove':
            return "path=(${path[@]:#" + ensure_quotes(self.visit(node.lhs)) + "})"
        if node.op == 'path_append':
            return f"path+=({ensure_quotes(self.visit(node.lhs))})"
        if node.op == 'path_prepend':
            return f"path=({ensure_quotes(self.visit(node.lhs))} $path)"

    def visit_ListOp(self, node):
        # For generic scalar list variables, we can't rely on having a tied array
        # as it happens for PATH/path
        # (see https://unix.stackexchange.com/questions/532148/what-is-the-difference-between-path-and-path-lowercase-versus-uppercase-with)
        if node.op == 'list_remove':
            return f"listremove {ensure_quotes(self.visit(node.rhs))} {self.visit(node.lhs)}"
        if node.op == 'list_append':
            return f"listappend {ensure_quotes(self.visit(node.rhs))} {self.visit(node.lhs)}"
        if node.op == 'list_prepend':
            return f"listprepend {ensure_quotes(self.visit(node.rhs))} {self.visit(node.lhs)}"

    def visit_default(self, node):
        return str(node)

def to_script(script):
    res = []
    visitor = BashVisitor()

    zsh_path_functions = """
# Inspired from http://www.linuxfromscratch.org/blfs/view/svn/postlfs/profile.html
# and ported to zsh.
# Functions to help us manage paths.  Second argument is the name of the
# list variable to be modified
listremove () {
        local PATHVARIABLE=${2}
        local array_helper
        local scalar_helper=${(P)PATHVARIABLE}

        typeset -T scalar_helper array_helper

        array_helper=(${array_helper[@]:#${1}})

        export $PATHVARIABLE=${scalar_helper}
}

listprepend () {
        local PATHVARIABLE=${2}
        local array_helper
        local scalar_helper=${(P)PATHVARIABLE}

        typeset -T scalar_helper array_helper

        array_helper=(${1} ${array_helper})

        export $PATHVARIABLE=${scalar_helper}
}

listappend () {
        local PATHVARIABLE=${2}
        local array_helper
        local scalar_helper=${(P)PATHVARIABLE}

        typeset -T scalar_helper array_helper

        array_helper+=(${1})

        export $PATHVARIABLE=${scalar_helper}
}
"""

    for cmd in script.cmds:
        res.append(visitor.visit(cmd))

    return zsh_path_functions + '\n'.join(res)
