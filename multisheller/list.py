from .cmds import Node
class ListOpNode:
	def __init__(self, op, lhs, rhs=None):
		self.op = op
		self.lhs = lhs
		self.rhs = rhs
