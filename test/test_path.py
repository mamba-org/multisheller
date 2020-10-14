import pytest
from utils import *
from multisheller import cmds, path, sys

@pytest.mark.parametrize("interpreter", get_interpreters())
def test_path_remove(tmp_path, interpreter):
    s = [
    	cmds.echo(cmds.env('PATH')),
    	sys.path_prepend("/tmp/abc"),
    	cmds.echo(cmds.env('PATH')),
    	sys.path_remove("/tmp/abc"),
    	cmds.echo(cmds.env('PATH')),
    	sys.path_prepend("/tmp/abc"),
    	sys.path_append("/tmp/abc"),
    	cmds.echo(cmds.env('PATH')),
    	sys.path_remove("/tmp/abc"),
    	cmds.echo(cmds.env('PATH')),
    ]
    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    print(stdout)
    print(stderr)
    lines = stdout.splitlines()
    assert(lines[0] == lines[2])
    assert('/tmp/abc' in lines[1])
    wtmp = lines[1]
    path_elems = wtmp.split(os.pathsep)
    assert(path_elems[0] == '/tmp/abc')

    assert('/tmp/abc' in lines[3])
    wtmp = lines[3]
    path_elems = wtmp.split(os.pathsep)
    assert(path_elems[0] == '/tmp/abc')
    assert(path_elems[-1] == '/tmp/abc')
    assert(lines[0] == lines[4])

@pytest.mark.parametrize("interpreter", get_interpreters())
def test_is_dir_file(tmp_path, interpreter):
    s = [
        emit_check(path.is_dir('/tmp')),
        emit_check(path.is_dir('/randomfolder')),
        emit_check(path.is_file('/tmp/randomfile')),
    ]
    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    print(stdout)
    print(stderr)
    lines = stdout.splitlines()
    assert(lines == ["YES", "NOPE", "NOPE"])

@pytest.mark.parametrize("interpreter", get_interpreters())
def test_path_join(tmp_path, interpreter):
    s = [
        cmds.echo(path.join('/tmp', 'test')),
    ]
    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    print(stdout)
    print(stderr)
    lines = [os.path.normpath(l) for l in stdout.splitlines()]
    assert(lines == ["/tmp/test"])