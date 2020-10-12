import re

class BinOpNode:
	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs

class EqNode(BinOpNode):
	def __str__(self):
		return f"{self.lhs} == {self.rhs}"

class AndNode(BinOpNode):
	def __str__(self):
		return f"{self.lhs} && {self.rhs}"

class OrNode(BinOpNode):
	def __str__(self):
		return f"{self.lhs} || {self.rhs}"

def and_(lhs, rhs):
	return AndNode(lhs, rhs)

def or_(lhs, rhs):
	return OrNode(lhs, rhs)

class Node:
	def __eq__(self, rhs):
		return CmpNode('eq', self, rhs)
	def __lt__(self, rhs):
		return CmpNode('lt', self, rhs)
	def __le__(self, rhs):
		return CmpNode('le', self, rhs)
	def __gt__(self, rhs):
		return CmpNode('gt', self, rhs)
	def __ge__(self, rhs):
		return CmpNode('ge', self, rhs)

class CmpNode(Node):
	def __init__(self, op, lhs, rhs):
		self.op = op
		self.lhs = lhs
		self.rhs = rhs
		self.opmap = {
			'eq': '==',
			'lt': '<',
			'le': '-le',
			'gt': '>',
			'ge': '-ge',
		}

	def __str__(self):
		return f"{self.lhs} {self.opmap[self.op]} {self.rhs}"

class EnvNode(Node):
	def __init__(self, varname):
		self.varname = varname

	def __str__(self):
		return "${}".format(self.varname)

def env(name):
	return EnvNode(name)

def StrNode(node):
	def __str__(self):
		return f"\"{self}\""

def str(val):
	return StrNode(val)

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

	def __str__(self):
		then_expr, else_expr = "", ""
		if self.then_expr:
			then_expr = f"\nthen\n    {self.then_expr}"
		if self.else_expr:
			else_expr = f"\nelse\n    {self.else_expr}"

		return f"if [[ {self.if_expr} ]];{then_expr}{else_expr}\nfi;"

def quoted(x):
	if x[0] == '"' or x[0] == '\'' and x[-1] == x[0]:
		return x
	else:
		return f"\"{re.escape(x)}\""

def ends_with(lhs, rhs):
	# TODO
	return f"{quoted(lhs)} == *{quoted(rhs)}"

def echo(x):
	return f"echo {x}"

def contains(lhs, rhs):
	# TODO
	return f"{quoted(lhs)} == *{quoted(rhs)}*"

def starts_with(lhs, rhs):
	# TODO
	# bash: [[ $TEST == "{rhs}"* ]]
	return f"{quoted(lhs)} == {quoted(rhs)}*"

def is_set(var):
	if type(var) is not EnvNode:
		var = EnvNode(var)
	return f"-z {var}"

def exit(code):
	return f"exit {code}"

class ExportNode:
	def __init__(self, var, rhs):
		self.var = var
		self.rhs = rhs

	def __str__(self):
		return f"export {self.var}={self.rhs}"

def export(lhs, rhs):
	return ExportNode(lhs, rhs)

def if_(expr):
	return ConditionalNode(expr)