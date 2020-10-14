import argparse, sys
import ast
from multisheller.cmds import *
from multisheller import path, sys
from multisheller.backend.utils import write_script
from pprint import pprint


def translate_file(f):
    with open(f) as fi:
        contents = fi.read()
    contents = contents
    tree = ast.parse(contents)

    ls = locals().copy()
    cmds = []
    for expr in tree.body:
        codeobj = compile(ast.Expression(expr.value), '<string>', mode='eval')
        res = eval(codeobj, globals(), ls)
        if type(expr) == ast.Assign:
            for t in expr.targets:
                ls.update({t.id: res})
        else:
            cmds.append(res)

    write_script('/tmp/', cmds, 'bash')
    with open('/tmp/script.sh') as fi:
        print(fi.read())
    write_script('/tmp/', cmds, 'powershell')
    with open('/tmp/script.ps1') as fi:
        print(fi.read())
    write_script('/tmp/', cmds, 'cmdexe')
    with open('/tmp/script.bat') as fi:
        print(fi.read())

def main():
    parser = argparse.ArgumentParser(
        description='A description of the cli program')
    parser.add_argument('file', type=str, help='file to translate')

    import sys
    parsed = parser.parse_args(sys.argv[1:])
    translate_file(parsed.file)
    return parsed


