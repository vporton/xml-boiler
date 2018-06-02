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

# import math

import networkx as nx

from xmlboiler.core.alg.path import GraphOfScripts
from xmlboiler.core.graph.minmax import Supremum
from xmlboiler.core.graph.path import shortest_pathes_to_edges


def _precedence(edge):
    return edge['script'].transformer.precedence

class ScriptsIterator(object):
    def __init__(self, state):
        self.state = state

    def __iter__(self):
        return self

    def __next__(self):
        self.available_chains = GraphOfScripts()  # TODO: inefficient? should hold the graph, not re-create it
        self.available_chains.add_scripts(self.state.scripts)
        self.available_chains.graph.add_node(self.state.opts.targetNamespaces)
        for source in self.state.all_namespaces:
            self.available_chains.graph.add_node(frozenset([source]))
        self.available_chains.adjust()
        first_edges = []
        for source in self.state.all_namespaces:
            # FIXME: Does not work with universal edges
            edges = self.available_chains.first_edges_for_shortest_path(self, frozenset([source]), self.state.opts.targetNamespaces)
            first_edges.extend(edges)
        if not first_edges:
            raise StopIteration

        executed = GraphOfScripts(self.state.executed_scripts)
        if self.check_has_executed(executed):
            self.available_chains = executed
            first_edges = []
            for source in self.state.all_namespaces:
                # FIXME: Does not work with universal edges
                edges = executed.first_edges_for_shortest_path(self, frozenset([source]), self.state.opts.targetNamespaces)
                first_edges.extend(edges)
            if len(first_edges) > 1:
                # TODO: Option to make it fatal
                self.state.execution_context.warning("More than one possible executed scripts.")

        # Choose the script among first_edges with highest precedence
        highest_precedences = self.state.graph.maxima(first_edges, key=lambda e: _precedence(e))
        highest_precedence_scripts = filter(lambda e: _precedence(e) in highest_precedences, first_edges)
        if len(highest_precedence_scripts) == 0:
            raise StopIteration
        if len(highest_precedence_scripts) == 1:  # TODO: right decision?
            self.state.executed_scripts.add(highest_precedence_scripts[0])
            return highest_precedence_scripts[0]

        # There are several highest_precedence_scripts - choose the maximal preservance and maximal priority
        minimal_preservance_paths = []
        for source in self.state.all_namespaces:
            minimal_preservance_paths.extend(nx.all_shortest_paths(frozenset([source]), self.state.opts.targetNamespaces,
                                                                   lambda v,u,e: Supremum(-e.script.base.preservance)))
        # a list of lists
        minimal_preservance_scripts = shortest_pathes_to_edges(self.available_chains.graph,
                                                               minimal_preservance_paths,
                                                               lambda e: Supremum(-e.script.base.preservance))
        minimal_preservance_scripts = [s.script for s in minimal_preservance_paths if 'script' in s]
        # FIXME: What if there is zero such paths?

        if highest_precedence_scripts in self.state.singletons:  # FIXME
            pass  # TODO
        raise StopIteration

    def check_has_executed(self, executed):
        for source in self.state.all_namespaces:
            for target in self.state.opts.targetNamespaces:  # FIXME: Check for the right var
                if nx.has_path(executed, source, target):
                    return True
        return False