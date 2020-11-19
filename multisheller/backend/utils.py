from multisheller import cmds
from multisheller.backend import bash, zsh, xonsh, cmdexe, powershell
import os

suffixes = {
    'cmdexe': '.bat',
    'bash': '.sh',
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

def write_script(path, commands, interpreter, fname='script'):
    s = cmds.Script(commands)
    fname = os.path.join(path, fname + suffixes[interpreter])

    with open(fname, 'w') as f:
        s = translators[interpreter].to_script(s)
        f.write(s)

    return fname
