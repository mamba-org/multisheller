import pytest
from multisheller import cmds
from utils import *

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
