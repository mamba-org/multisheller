from .path import PathOpNode
from .list import ListOpNode

def path_remove(p):
	return PathOpNode('path_remove', p)

def path_append(p):
	return PathOpNode('path_append', p)

def path_prepend(p):
	return PathOpNode('path_prepend', p)

def list_remove(l, v):
	return ListOpNode('list_remove', l, v)

def list_append(l, v):
	return ListOpNode('list_append', l, v)

def list_prepend(l, v):
	return ListOpNode('list_prepend', l, v)