#  Copyright (c) 2018 Victor Porton,
#  XML Boiler - http://freesoft.portonvictor.org
#
#  This file is part of XML Boiler.
#
#  XML Boiler is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

# Finding shortest paths in (weighted) digraph of enriched scripts.
# Vertices are finite sets of namespaces.

# For now we re-run the search completely if new edges are added.
# We also add to the graph nodes (i, j, weight=0) where i<=j are sets of namespaces.

import networkx as nx

from xmlboiler.core.alg.state import EnrichedScript


# TODO: Wrap it also with "double graph" (https://cs.stackexchange.com/a/96348/39512) to have no adjanced
# edges from graph2 (to increase the performance by reducing the number of paths of the same weight).
class GraphWithProxy(object):
    """
    We have two directed multigraphs. A traversal must has at least one edge of the first graph.

    https://cs.stackexchange.com/a/96348/39512 for the algorithm.

    i^- is represented as (0, i) and i^+ is represented as (1, i)
    """
    def __init__(self, graph1, graph2):
        self.composite_graph = nx.MultiDiGraph()
        self.graph1 = graph1
        self.graph2 = graph2

    def adjust(self):
        for u in self.graph1.nodes():
            # TODO: Need both 0 and 1?
            self.composite_graph.add_node((0, u))
            self.composite_graph.add_node((1, u))
        for u, v, d in self.graph1.edges(data=True):
            self.composite_graph.add_edge((0, u), (1, v), attr_dict=d)
            self.composite_graph.add_edge((1, u), (1, v), attr_dict=d)
        for u, v, d in self.graph2.edges(data=True):
            self.composite_graph.add_edge((0, u), (0, v), attr_dict=d)
            self.composite_graph.add_edge((1, u), (1, v), attr_dict=d)

    def all_shortest_paths(self, source, target, weight=None):
        return nx.all_shortest_paths(self.composite_graph, (0, source), (1, target), weight)


# TODO: Silly logic
class GraphOfScripts(object):
    def __init__(self, graph, universal_precedence, precedences_graph):
        self.universal_precedence = universal_precedence
        self.precedences_graph = precedences_graph
        self.graph1 = graph or nx.MultiDiGraph()

    def add_scripts(self, enriched_scripts):
        for scr in enriched_scripts:
            source = frozenset(scr.base.transformer.source_namespaces)
            target = frozenset(scr.base.transformer.target_namespaces)
            # TODO: There are two proposed formulas for weight in the specification
            weight = 1 / (scr.base.preservance + scr.base.stability + scr.base.preference)
            if scr.base.transformer.universal and \
                    self.precedences_graph.is_connected(self.universal_precedence, scr.base.transformer.precedence):
                target = frozenset()
            self.graph1.add_edge(source, target, script=scr, weight=weight)

    # to be called before use
    def adjust(self):
        self.graph2 = nx.MultiDiGraph()
        # TODO: The below is inefficient
        for i in self.graph1.nodes:
            for j in self.graph1.nodes:
                if i < j:
                    if not self.graph2.has_edge(i, j):
                        self.graph2.add_edge(i, j, weight=0)
        self.graph = GraphWithProxy(self.graph1, self.graph2)
        self.graph.adjust()

    def all_shortest_paths(self, source, target, weight=None):
        return self.graph.all_shortest_paths(source, target, weight)

    # def first_edges_for_shortest_path(self, source, target):
    #     paths = nx.all_shortest_paths(self.graph, source, target, weight='weight')
    #     edges = []
    #     try:
    #         # What if path is empty (or empty after removing interset edges)?
    #         for path in paths:
    #             script_found = False
    #             for i in range(len(path) - 1):
    #                 if script_found:
    #                     break
    #                 for _, edge in self.graph[path[i]][path[i+1]].items():
    #                     script = edge.get('script')
    #                     if script is not None:
    #                         edges.append(script)
    #                         script_found = True
    #                         break
    #     except nx.NetworkXNoPath:
    #         pass
    #     return edges
