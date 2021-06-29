import pytest
from pathlib import Path
from utils import *
from multisheller import cmds, path, sys

@pytest.mark.parametrize("interpreter", get_interpreters())
def test_path_remove(tmp_path, interpreter):
    if running_os == 'win':
        fake_path = 'C:\\Users\\bin'
        weird_path = "C:\\tmp\\Programs (y75)\\"
    else:
        fake_path = "/tmp/abc"
        weird_path = "/tmp/Programs (y75)/"
    s = [
    	cmds.echo(cmds.env('PATH')),
    	sys.path_prepend(fake_path),
    	cmds.echo(cmds.env('PATH')),
    	sys.path_remove(fake_path),
    	cmds.echo(cmds.env('PATH')),
    	sys.path_prepend(fake_path),
    	sys.path_append(fake_path),
    	cmds.echo(cmds.env('PATH')),
    	sys.path_remove(fake_path),
    	cmds.echo(cmds.env('PATH')),
        sys.path_prepend(weird_path),
        sys.path_remove(weird_path),
        cmds.echo(cmds.env('PATH')),
    ]
    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    print(stdout)
    print(stderr)
    lines = stdout.splitlines()
    assert(lines[0] == lines[2])
    assert(fake_path in lines[1])
    wtmp = lines[1]
    path_elems = wtmp.split(os.pathsep)
    assert(path_elems[0] == fake_path)

    assert(fake_path in lines[3])
    wtmp = lines[3]
    path_elems = wtmp.split(os.pathsep)
    assert(path_elems[0] == fake_path)
    assert(path_elems[-1] == fake_path)
    assert(lines[0] == lines[4])
    assert(lines[0] == lines[5])

@pytest.mark.parametrize("interpreter", get_interpreters())
@pytest.mark.parametrize("env_variable_name", ['RANDOM_LIST_ENV_VAR_DIRS', 'RANDOM_LIST_ENV_VAR'])
def test_list_remove(tmp_path, interpreter, env_variable_name):
    if running_os == 'win':
        preexisting_path = 'C:\\Users\\lib'
        fake_path = 'C:\\Users\\bin'
        weird_path = "C:\\tmp\\Programs (y75)\\"
    else:
        preexisting_path = "/tmp/lib"
        fake_path = "/tmp/abc"
        weird_path = "/tmp/Programs (y75)/"
    s = [
        sys.list_prepend(env_variable_name, preexisting_path),
        cmds.echo(cmds.env(env_variable_name)),
        sys.list_prepend(env_variable_name, fake_path),
        cmds.echo(cmds.env(env_variable_name)),
        sys.list_remove(env_variable_name, fake_path),
        cmds.echo(cmds.env(env_variable_name)),
        sys.list_prepend(env_variable_name, fake_path),
        sys.list_append(env_variable_name, fake_path),
        cmds.echo(cmds.env(env_variable_name)),
        sys.list_remove(env_variable_name, fake_path),
        cmds.echo(cmds.env(env_variable_name)),
        sys.list_prepend(env_variable_name, weird_path),
        sys.list_remove(env_variable_name, weird_path),
        cmds.echo(cmds.env(env_variable_name)),
    ]
    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    print(stdout)
    print(stderr)
    lines = stdout.splitlines()
    assert(lines[0] == lines[2])
    assert(fake_path in lines[1])
    wtmp = lines[1]
    path_elems = wtmp.split(os.pathsep)
    assert(path_elems[0] == fake_path)

    assert(fake_path in lines[3])
    wtmp = lines[3]
    path_elems = wtmp.split(os.pathsep)
    assert(path_elems[0] == fake_path)
    assert(path_elems[-1] == fake_path)
    assert(lines[0] == lines[4])
    assert(lines[0] == lines[5])

@pytest.mark.parametrize("interpreter", get_interpreters())
def test_is_dir_file(tmp_path, interpreter):
    if running_os == 'win':
        existing_folder = 'C:\\Users'
    else:
        existing_folder = '/tmp'

    s = [
        emit_check(path.is_dir(existing_folder)),
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
    lines = [Path(l) for l in stdout.splitlines()]
    assert(lines == [Path("/tmp/test")])
    
@pytest.mark.parametrize("interpreter", get_interpreters())
def test_path_join_expanding_env_var(tmp_path, interpreter):
    s = [
        cmds.export("TMP_PREFIX", "/tmp"),
        cmds.export("TMP_PREFIX_TEST", path.join(cmds.env("TMP_PREFIX"), "test")),
        cmds.echo(cmds.env("TMP_PREFIX_TEST")),
    ]
    stdout, stderr = call_interpreter(s, tmp_path, interpreter)
    print(stdout)
    print(stderr)
    lines = [Path(l) for l in stdout.splitlines()]
    assert(lines == [Path("/tmp/test")])
