import subprocess
import sys, os

from multisheller import cmds
from multisheller.backend import bash, zsh, xonsh, cmdexe, powershell

def emit_check(cond):
    return cmds.if_(cond).then_(cmds.echo("YES")).else_(cmds.echo("NOPE"))

suffixes = {
    'cmdexe': '.bat',
    'bash': '.sh',
    'zsh': '.sh',
    'xonsh': '.sh',
    'powershell': '.ps1',
}

translators = {
    'cmdexe': cmdexe,
    'bash': bash,
    'zsh': zsh,
    'xonsh': xonsh,
    'powershell': powershell,
}

enable_on_os = {
    'win': {'powershell', 'cmdexe'},
    'unix': {'bash', 'zsh', 'xonsh'},
}

if os.name == 'nt':
    running_os = 'win'
else:
    running_os = 'unix'

def write_script(path, commands, interpreter):
    s = cmds.Script(commands)
    fname = os.path.join(path, 'script' + suffixes[interpreter])

    with open(fname, 'w') as f:
        s = translators[interpreter].to_script(s)
        print(s)
        f.write(s)

    return fname

def call_interpreter(s, tmp_path, interpreter):
    f = write_script(tmp_path, s, interpreter)
    if interpreter not in enable_on_os[running_os]:
        return None, None

    if interpreter == 'cmdexe':
        res = subprocess.run(['cmd.exe', '/C', f], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    elif interpreter == 'powershell':
        res = subprocess.run(["powershell.exe", "-File", f], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    else:
        res = subprocess.run([interpreter, f], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    stdout = res.stdout.decode('utf-8').strip()
    stderr = res.stderr.decode('utf-8').strip()
    return stdout, stderr

def get_interpreters(exclude=[]):
    return [x for x in enable_on_os[running_os] if x not in exclude]
