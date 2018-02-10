# Directed graph with at most one edge between vertices
class Graph(object):
    def __init__(self, adj=None):
        """
        :param adj: a dict from vertice to vertex set
        """
        adj = dict() if adj is None else adj

    def __eq__(self, other):
        return self.adj == other.adj

    def __hash__(self):
        return hash(self.adj)

    def add_edge(self, src, dst):
        value = self.adj.get(src, None)
        if value is None:
            self.adj[src] = {dst}
        else:
            value.append(dst)

    def adjanced(self, src, dst):
        s = self.adj.get(src, None)
        if s is None:
            return False
        return dst in s

    def reverse(self):
        result = Graph()
        for key, value in self.adj.items():
            for y in value:
                result.add_edge(y, key)
        return result
