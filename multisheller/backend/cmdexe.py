from .visitor import NodeVisitor
from .common import join_expr
import re

def ensure_quotes(x):
    if x[0] == '"' or x[0] == '\'' and x[-1] == x[0]:
      return x
    else:
      return f"\"{(x)}\""


def generate_function_to_remove_element_from_list(functionName, listName):
    """Generate a Batch script function to remove element from a list.

    As in Batch scripts it is not possible to dereference twice a variable,
    it is easier to generate a function for each variable from which we want
    to remove an element.

    Keyword arguments:
    functionName -- the function name
    listName -- the name of the environment variable that contains the list
    """
    return f"""
@REM code below borrowed from https://stackoverflow.com/a/1430570 (CC-BY-SA 2.5)
@REM Author: Cheeso, Sep 16, 2009

:{functionName}
SETLOCAL ENABLEDELAYEDEXPANSION

@REM  ~fs = remove quotes, full path, short names
set fqElement=%~fs1

@REM convert path to a list of quote-delimited strings, separated by spaces
set fpath="%{listName}:;=" "%"

@REM iterate through those path elements
for %%p in (%fpath%) do (
    @REM  ~fs = remove quotes, full path, short names
    set p2=%%~fsp
    @REM is this element NOT the one we want to remove?
    if /i NOT "!p2!"=="%fqElement%" (
        if _!tpath!==_ (set tpath=%%~p) else (set tpath=!tpath!;%%~p)
    )
)

set {listName}=!tpath!
ENDLOCAL & set {listName}=%tpath%
goto :EOF
"""


class CmdExeVisitor(NodeVisitor):
    def __init__(self):
        # This is the lists for which we need to
        # generate a remove function
        self.list_with_remove_functions = set([])

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
            then_expr = f"(\n{join_expr(op.then_expr, self.visit)}\n)"
        if op.else_expr:
            else_expr = f" else (\n{join_expr(op.else_expr, self.visit)}\n)"

        return f"if {self.visit(op.if_expr)} {then_expr}{else_expr}\n"

    def visit_PathOp(self, node):
        q = ensure_quotes
        if node.op == 'join':
            return f"{self.visit(node.lhs)}\\{self.visit(node.rhs)}"
        elif node.op == 'is_file':
            return f"exist {self.visit(node.lhs)}"
        if node.op == 'is_dir':
            return f"exist {self.visit(node.lhs)}"
        if node.op == 'path_remove':
            return f"call :removeFromPath {ensure_quotes(self.visit(node.lhs))}"
        if node.op == 'path_append':
            return f"set PATH=%PATH%;{self.visit(node.lhs)}"
        if node.op == 'path_prepend':
            return f"set PATH={self.visit(node.lhs)};%PATH%"

    def visit_ListOp(self, node):
        if node.op == 'list_remove':
            self.list_with_remove_functions.add(self.visit(node.lhs))
            return f"call :removeFrom{self.visit(node.lhs)}List {ensure_quotes(self.visit(node.rhs))}"
        if node.op == 'list_append':
            return f"set {self.visit(node.lhs)}=%{self.visit(node.lhs)}%;{self.visit(node.rhs)}"
        if node.op == 'list_prepend':
            return f"set {self.visit(node.lhs)}={self.visit(node.rhs)};%{self.visit(node.lhs)}%"

    def visit_Call(self, op):
        if op.cmd == 'echo':
            # return f"{op.cmd} {ensure_quotes(' '.join(op.args))}"
            pass
        return f"{op.cmd} {' '.join([self.visit(arg) for arg in op.args])}"

    def visit_default(self, node):
        return str(node)


def to_script(script):
    res = []
    visitor = CmdExeVisitor()

    # Preable
    res.append("""
@echo off
goto start:
""")

    # Function to remove element from path
    res.append(generate_function_to_remove_element_from_list("removeFromPath", "PATH"))

    # We first visit the cmd graph to populate list_with_remove_functions
    # but we add it in the separate list as we need to put those after the function definitions
    resCmds = []
    for cmd in script.cmds:
        resCmds.append(visitor.visit(cmd))

    # Generate to remove element from any other list variable
    for listVariable in visitor.list_with_remove_functions:
        res.append(generate_function_to_remove_element_from_list(f"removeFrom{listVariable}List", listVariable))

    res.append(":start")

    # Add the already generated scripts
    res.extend(resCmds)

    return '\n'.join(res)