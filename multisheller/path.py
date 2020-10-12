
# put in module path
def join(lhs, rhs):
	# TODO return node
	return f"{lhs}/{rhs}"

def is_file(p):
	return f"test -f {p}"

def is_dir(p):
	return f"test -d {p}"