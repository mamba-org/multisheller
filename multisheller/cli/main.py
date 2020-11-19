import argparse, sys
import ast
import os
from multisheller.cmds import *
from multisheller import path, sys
from multisheller.backend.utils import write_script
from pprint import pprint

from rich.console import Console
from rich.syntax import Syntax
from rich.rule import Rule

console = Console()

def translate_file(f):
    fname = os.path.basename(f)
    folder = os.path.abspath(os.path.dirname(fname))
    fname_base = os.path.splitext(fname)[0]

    console.print("[green]Generating scripts for [bold]bash, zsh, powershell, cmd.exe[/bold]")
    console.print(f"[green]Placing files in: {folder}")

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

    lang_to_syntax = {
        'powershell': 'ps1',
        'cmdexe': 'bat',
        'bash': 'bash',
        'zsh': 'zsh',
        'xonsh': 'xonsh'
    }

    def write_out(lang):
        script_file = write_script(folder, cmds, lang, fname=fname_base)
        with open(script_file) as fi:
            console.print(Rule(f'{os.path.basename(script_file)} | {lang}'))
            console.print(Syntax(fi.read(), lang_to_syntax[lang]))

    for x in ['bash', 'powershell', 'cmdexe', 'zsh', 'xonsh']:
        write_out(x)
        print('\n')



    # script_file = write_script(folder, cmds, 'powershell', fname=fname_base)
    # with open(script_file) as fi:
    #     print('\n')
    #     console.print(Rule('script.ps1 | PowerShell'))
    #     console.print(Syntax(fi.read(), 'ps1'))
    # script_file = write_script(folder, cmds, 'cmdexe', fname=fname_base)
    # with open(script_file) as fi:
    #     print('\n')
    #     console.print(Rule('script.bat | cmd.exe'))
    #     console.print(Syntax(fi.read(), 'bat'))

def main():
    parser = argparse.ArgumentParser(
        description='A description of the cli program')
    parser.add_argument('file', type=str, help='file to translate')

    import sys
    parsed = parser.parse_args(sys.argv[1:])
    translate_file(parsed.file)
