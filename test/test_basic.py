import tempfile
import subprocess
import sys, os
import pytest

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

@pytest.mark.parametrize("interpreter", get_interpreters())
def test_hello_world(tmp_path, interpreter):
    s = [cmds.echo("hello world")]
    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    assert (stdout == "hello world")

@pytest.mark.parametrize("interpreter", get_interpreters())
def test_if_else(tmp_path, interpreter):
    s = [
        cmds.export("somevar", "1000"),
        cmds.if_(cmds.env("somevar") == "1000").then_(
            cmds.echo("YES")
        )
    ]

    stdout, stderr = call_interpreter(s, tmp_path, interpreter)

    assert (stdout == "YES")

    s = [
        cmds.export("somevar", "1000"),
        cmds.if_(cmds.env("somevar") == "1010").then_(
            cmds.echo("YES")
        ).else_(
            cmds.echo("NOPE")
        )
    ]

    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    assert (stdout == "NOPE")

@pytest.mark.parametrize("interpreter", get_interpreters(exclude=['powershell', 'cmdexe']))
def test_startwsith_endswith(tmp_path, interpreter):
    def check(expr):
        return cmds.if_(expr).then_(cmds.echo("YES")).else_(cmds.echo("NO"))

    s = [
        check(cmds.starts_with("ITSATEST", "ITSA")),
        check(cmds.ends_with("ITSATEST", "TEST")),
        check(cmds.contains("ITSATEST", "ATE"))
    ]

    stdout, stderr = call_interpreter(s, tmp_path, interpreter)

    assert (stdout.splitlines() == ["YES"] * 3)

@pytest.mark.parametrize("interpreter", get_interpreters(exclude=['cmdexe']))
def test_and_or(tmp_path, interpreter):
    s = [
        cmds.export("somevar", "1"),
        cmds.export("othervar", "1"),
        cmds.if_(cmds.and_(cmds.env("somevar") == "1", cmds.env("othervar"))).then_(
            cmds.echo("YES")
        ),
        cmds.if_(cmds.and_(cmds.is_set("somevar"), cmds.is_set("nope"))).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
        cmds.if_(cmds.or_(cmds.is_set("somevar"), cmds.is_set("nope"))).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
    ]

    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    assert (stdout.splitlines() == ["YES", "NOPE", "YES"])

@pytest.mark.parametrize("interpreter", get_interpreters())
def test_cmp(tmp_path, interpreter):
    s = [
        cmds.export("somevar", "123"),
        cmds.if_(cmds.env("somevar") >= 100).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
        cmds.if_(cmds.env("somevar") <= 100).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
        cmds.if_(cmds.env("somevar") > 100).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
        cmds.if_(cmds.env("somevar") < 100).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
    ]

    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    assert (stdout.splitlines() == ["YES", "NOPE"] * 2)

@pytest.mark.parametrize("interpreter", get_interpreters())
def test_is_set(tmp_path, interpreter):
    s = [
        cmds.unset(cmds.env("somevar")),
        emit_check(cmds.is_set(cmds.env("somevar"))),
        # emit_check(cmds.is_set(cmds.var("somevar"))),
        cmds.export("somevar", 100),
        emit_check(cmds.is_set(cmds.env("somevar"))),
        # emit_check(cmds.is_set(cmds.var("somevar"))),
    ]
    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    assert (stdout.splitlines() == ["NOPE", "YES"])
