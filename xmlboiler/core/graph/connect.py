from xmlboiler.core.graph.base import union, square, Graph


def transitive_closure(graph):
    while True:
        result = union(graph, square(graph))
        if result == graph:
            return result
        graph = result


class Connectivity(object):
    def __init__(self):
        self.connectivity = Graph()

    def is_connected(self, src, dst):
        return self.connectivity.adjanced(src, dst)

    def add_graph(self, g):
        self.connectivity = transitive_closure(union(self.connectivity, g))
