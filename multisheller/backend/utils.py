from multisheller import cmds
from multisheller.backend import bash, zsh, xonsh, cmdexe, powershell
import os

suffixes = {
    'cmdexe': '.bat',
    'bash': '.bash',
    'zsh': '.zsh',
    'xonsh': '.xsh',
    'powershell': '.ps1',
}

translators = {
    'cmdexe': cmdexe,
    'bash': bash,
    'zsh': zsh,
    'xonsh': xonsh,
    'powershell': powershell,
}

def write_script(path, commands, interpreter, filename_without_extension='script'):
    s = cmds.Script(commands)
    fname = os.path.join(path, filename_without_extension + suffixes[interpreter])

    with open(fname, 'w') as f:
        s = translators[interpreter].to_script(s)
        f.write(s)

    return fname

# See https://github.com/mamba-org/multisheller/issues/11
def write_bash_zsh_disambiguation_script(path, filename_without_extension='script'):
    fname = os.path.join(path, filename_without_extension + '.sh')

    with open(fname, 'w') as f:
        f.write(r'if [ ! -z "$ZSH_VERSION" ]; then')
        f.write('\n')
        f.write(r'  SCRIPT_DIR=${0:a:h}')
        f.write('\n')
        f.write(r'  SCRIPT_NAME=$(basename "${(%):-%x}")')
        f.write('\n')
        f.write(r'  SCRIPT_NAME_WITHOUT_EXT=${SCRIPT_NAME%.*}')
        f.write('\n')
        f.write(r'  source ${SCRIPT_DIR}/${SCRIPT_NAME_WITHOUT_EXT}.zsh')
        f.write('\n')
        f.write("else\n")
        f.write(r'  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"')
        f.write('\n')
        f.write(r'  SCRIPT_NAME=$(basename "${BASH_SOURCE[0]}")')
        f.write('\n')
        f.write(r'  SCRIPT_NAME_WITHOUT_EXT=${SCRIPT_NAME%.*}')
        f.write('\n')
        f.write(r'  source ${SCRIPT_DIR}/${SCRIPT_NAME_WITHOUT_EXT}.bash')
        f.write('\n')
        f.write('fi\n')

    f.close()

    return