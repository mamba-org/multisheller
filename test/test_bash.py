import tempfile
import subprocess
import sys, os
sys.path.append(os.path.dirname(__file__) + '/..')

from multisheller import cmds

def write_script(path, name, commands):
	fname = os.path.join(path, name + '.sh')
	with open(fname, 'w') as f:
		for cmd in commands:
			print(str(cmd))
			f.write(str(cmd))
			f.write('\n')
	return fname

def call_bash(f):
	res = subprocess.run(["bash", f], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
	stdout = res.stdout.decode('utf-8').strip()
	stderr = res.stderr.decode('utf-8').strip()
	return stdout, stderr

def test_hello_world(tmp_path):
	s = write_script(tmp_path, 'hello_world', [
		cmds.echo("hello world")
	])
	stdout, stderr = call_bash(s)
	assert (stdout == "hello world")

def test_if_else(tmp_path):
	s = write_script(tmp_path, 'test_if_else', [
		cmds.export("somevar", "1000"),
		cmds.if_(cmds.env("somevar") == "1000").then_(
			cmds.echo("YES")
		)
	])

	stdout, stderr = call_bash(s)
	assert (stdout == "YES")

	s = write_script(tmp_path, 'test_if_else', [
		cmds.export("somevar", "1000"),
		cmds.if_(cmds.env("somevar") == "1010").then_(
			cmds.echo("YES")
		).else_(
			cmds.echo("NOPE")
		)
	])

	stdout, stderr = call_bash(s)
	assert (stdout == "NOPE")

def test_startwsith_endswith(tmp_path):
	def check(expr):
		return cmds.if_(expr).then_(cmds.echo("YES")).else_(cmds.echo("NO"))


	s = write_script(tmp_path, 'test_if_else', [
		check(cmds.starts_with("ITSATEST", "ITSA")),
		check(cmds.ends_with("ITSATEST", "TEST")),
		check(cmds.contains("ITSATEST", "ATE"))
	])

	stdout, stderr = call_bash(s)
	assert (stdout.splitlines() == ["YES"] * 3)


def test_and_or(tmp_path):
	s = write_script(tmp_path, 'test_if_else', [
		cmds.export("somevar", "1"),
		cmds.export("othervar", "1"),
		cmds.if_(cmds.and_(cmds.env("somevar") == "1", cmds.env("othervar"))).then_(
			cmds.echo("YES")
		),
		cmds.if_(cmds.and_(cmds.is_set("somevar"), cmds.is_set("nope"))).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
		cmds.if_(cmds.or_(cmds.is_set("somevar"), cmds.is_set("nope"))).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
	])

	stdout, stderr = call_bash(s)
	assert (stdout.splitlines() == ["YES", "NOPE", "YES"])

def test_cmp(tmp_path):
	s = write_script(tmp_path, 'test_if_else', [
		cmds.export("somevar", "123"),
		cmds.if_(cmds.env("somevar") >= 100).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
		cmds.if_(cmds.env("somevar") <= 100).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
		cmds.if_(cmds.env("somevar") > 100).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
		cmds.if_(cmds.env("somevar") < 100).then_(cmds.echo("YES")).else_(cmds.echo("NOPE")),
	])

	stdout, stderr = call_bash(s)
	assert (stdout.splitlines() == ["YES", "NOPE"] * 2)

# if __name__ == '__main__':
# 	test_answer()