import argparse, sys
import ast
import os
from multisheller.cmds import *
from multisheller import path, sys
from multisheller.backend.utils import write_script
from multisheller.backend.utils import write_bash_zsh_disambiguation_script
from pprint import pprint


def translate_file(f, output):
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

    # Generate scripts
    generation_directory, name_without_extension = os.path.split(output)

    write_script(generation_directory, cmds, "cmdexe", name_without_extension)
    write_script(generation_directory, cmds, "bash", name_without_extension)
    write_script(generation_directory, cmds, "zsh", name_without_extension)
    write_script(generation_directory, cmds, "xonsh", name_without_extension)
    write_script(generation_directory, cmds, "powershell", name_without_extension)

    # Conda do not explicitly support different activation scripts for zsh and bash,
    # so we generate them as .bash and .zsh (ignored by conda) and then generate a
    # small .sh script to source the correct one depending on the used shell
    # See https://github.com/mamba-org/multisheller/issues/11
    write_bash_zsh_disambiguation_script(generation_directory, name_without_extension)

def main():
    parser = argparse.ArgumentParser(
        description='multisheller cli tool to transform multisheller files in shell-specific scripts.')
    parser.add_argument('file', type=str, help='multisheller file to translate')
    parser.add_argument('--output', nargs='?', type=str, help='location of the output files, without extensions (default: input file without extension)')

    import sys
    parsed = parser.parse_args(sys.argv[1:])
    if parsed.output is not None:
        output = parsed.output
    else:
        filename_without_extension, file_extension = os.path.splitext(parsed.file)
        output = filename_without_extension

    translate_file(parsed.file, output)
    return 0
