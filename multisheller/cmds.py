import re

class Script:
	def __init__(self, cmd_list):
		self.cmds = cmd_list

class BinOpNode:
	def __init__(self, op, lhs, rhs):
		self.op  = op
		self.lhs = lhs
		self.rhs = rhs

class UnaryOpNode:
	def __init__(self, op, value):
		self.op  = op
		self.value = value

def and_(lhs, rhs):
	return BinOpNode('and', lhs, rhs)

def or_(lhs, rhs):
	return BinOpNode('or', lhs, rhs)

def not_(node):
	return UnaryOpNode('not', rhs)

class Node:
	def __eq__(self, rhs):
		return BinOpNode('eq', self, rhs)
	def __lt__(self, rhs):
		return BinOpNode('lt', self, rhs)
	def __le__(self, rhs):
		return BinOpNode('le', self, rhs)
	def __gt__(self, rhs):
		return BinOpNode('gt', self, rhs)
	def __ge__(self, rhs):
		return BinOpNode('ge', self, rhs)

class VarNode(Node):
	def __init__(self, varname):
		self.varname = varname

class EnvNode(VarNode):
	pass

def env(name):
	return EnvNode(name)

def var(name):
	return VarNode(name)

# class StrNode(Node):
# 	def __init__(self, val):
# 		return f"\"{val}\""

# def str(val):
# 	return StrNode(val)

class ConditionalNode:
	def __init__(self, if_expr):
		self.if_expr = if_expr
		self.then_expr = None
		self.else_expr = None
	# implement wwiht reipeated __call__?
	def then_(self, expr):
		self.then_expr = expr
		return self

	def else_(self, expr):
		self.else_expr = expr
		return self

class StrOpNode(Node):
	def __init__(self, op, lhs, rhs=None):
		self.op = op
		self.lhs = lhs
		self.rhs = rhs

def quoted(x):
	return StrOpNode('quote', x)

def ends_with(lhs, rhs):
	return StrOpNode('ends_with', lhs, rhs)

def contains(lhs, rhs):
	return StrOpNode('contains', lhs, rhs)

def starts_with(lhs, rhs):
	return StrOpNode('starts_with', lhs, rhs)

def is_set(var):
	if type(var) is not EnvNode:
		var = EnvNode(var)
	return UnaryOpNode('is_set', var)
	# return f"-z {var}"

class CallNode(Node):
	def __init__(self, cmd, args):
		self.cmd = cmd
		self.args = args

def echo(x):
	return CallNode('echo', [x])

def exit(code):
	return CallNode('exit', [code])

def export(lhs, rhs):
	return BinOpNode('export', lhs, rhs)

def unset(var):
	return UnaryOpNode('unset', var)

def if_(expr):
	return ConditionalNode(expr)