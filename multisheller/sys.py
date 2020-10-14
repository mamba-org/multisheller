from .path import PathOpNode

def path_remove(p):
	return PathOpNode('path_remove', p)

def path_append(p):
	return PathOpNode('path_append', p)

def path_prepend(p):
	return PathOpNode('path_prepend', p)