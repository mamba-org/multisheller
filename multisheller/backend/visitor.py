class NodeVisitor:
    """Base node visitor class"""

    def __init__(self, root=None):
        """
        Parameters
        ----------
        node : Node or None
        """
        self.root = root

    def visit(self, node=None):
        """Visit the tree or node"""
        # node = self.root if node is None else node
        meth_name = "visit_" + node.__class__.__name__[:-len("Node")]
        meth = getattr(self, meth_name, self.visit_default)
        rtn = meth(node)
        return rtn

    def visit_default(self, node):
        raise NotImplementedError(
            self.__class__.__name__ +
            " does not implement visit_default() or visit_" +
            self.__class__.__name__ +
            "()."
        )
