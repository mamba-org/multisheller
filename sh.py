class EqNode:
	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs

	def __str__(self):
		return f"{self.lhs} == {self.rhs}"

class EnvNode:
	def __init__(self, varname):
		self.varname = varname

	def __str__(self):
		return "${}".format(self.varname)

	def __eq__(self, rhs):
		return EqNode(self, rhs)

def env(name):
	return EnvNode(name)

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
			then_expr = f"\nthen;\n    {self.then_expr}"
		if self.else_expr:
			else_expr = f"\nelse;\n    {self.then_expr}"

		return f"if [ {self.if_expr} ];{then_expr}{else_expr}\nfi;"

def path_join(lhs, rhs):
	# TODO return node
	return f"{lhs}/{rhs}"

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