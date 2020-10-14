from .cmds import Node
class PathOpNode:
	def __init__(self, op, lhs, rhs=None):
		self.op = op
		self.lhs = lhs
		self.rhs = rhs

# put in module path
def join(lhs, rhs):
	# TODO return node
	return PathOpNode('join', lhs, rhs)
	# return f"{lhs}/{rhs}"

def is_file(p):
	return PathOpNode('is_file', p)
	# return f"test -f {p}"

def is_dir(p):
	return PathOpNode('is_dir', p)
	# return f"test -d {p}"