import tempfile
import subprocess
import sys, os
sys.path.append(os.path.dirname(__file__) + '/..')

from multisheller import cmds
from multisheller.backend import cmdexe

def write_script(path, name, commands):
	s = cmds.Script(commands)
	fname = os.path.join(path, name + '.sh')
	with open(fname, 'w') as f:
		s = cmdexe.to_script(s)
		print(s)
		f.write(s)
	return fname

def call_interpreter(f):
	return "", ""
	pass
	# res = subprocess.run(["bash", f], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
	# stdout = res.stdout.decode('utf-8').strip()
	# stderr = res.stderr.decode('utf-8').strip()
	# return stdout, stderr

def test_hello_world(tmp_path):
	s = write_script(tmp_path, 'hello_world', [
		cmds.echo("hello world")
	])
	stdout, stderr = call_interpreter(s)
	# assert (stdout == "hello world")

def test_if_else(tmp_path):
	s = write_script(tmp_path, 'test_if_else', [
		cmds.export("somevar", "1000"),
		cmds.if_(cmds.env("somevar") == "1000").then_(
			cmds.echo("YES")
		)
	])

	stdout, stderr = call_interpreter(s)
	# assert (stdout == "YES")

	s = write_script(tmp_path, 'test_if_else', [
		cmds.export("somevar", "1000"),
		cmds.if_(cmds.env("somevar") == "1010").then_(
			cmds.echo("YES")
		).else_(
			cmds.echo("NOPE")
		)
	])

	stdout, stderr = call_interpreter(s)
	# assert (stdout == "NOPE")
