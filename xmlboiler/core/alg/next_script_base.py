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

from abc import ABC, abstractmethod

import networkx as nx
from rdflib import URIRef

from xmlboiler.core.alg.path import GraphOfScripts
from xmlboiler.core.graph.minmax import Supremum
from xmlboiler.core.graph.path import shortest_lists_of_edges, shortest_paths_to_edges


class ScriptsIteratorBase(ABC):
    def __init__(self, state):
        self.state = state

    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self):
        pass

    def _next_outer_script(self):
        parents = [self.state.dom.documentElement]
        # depth-first search
        while parents:
            v = parents.pop()
            scripts = self._outer_node_script(v)
            if scripts:
                scripts = self._choose_by_preservance_priority(scripts)
                return scripts[0][0]  # TODO: What if there is several of the same rating?
            for w in v.childNodes:
                parents.append(w)
        return None

    def _checked_scripts(self, scripts):
        if self.state.executed_scripts.isdisjoint(scripts):
            return scripts
        return self.state.executed_scripts.intersection(scripts)

    def _available_chains(self, sources):  # TODO: `destinations` not used
        # TODO: inefficient? should hold the graph, not re-create it
        available_chains = GraphOfScripts(None, self.state.opts.universal_precedence, self.state.precedences_higher)
        # available_chains.add_scripts(frozenset(frozenset(self._checked_scripts(self.state.scripts)) - self.state.failed_scripts))  # slow
        available_chains.add_scripts(frozenset(frozenset(self.state.scripts) - self.state.failed_scripts))  # slow

        available_chains.graph1.add_node(self.state.opts.target_namespaces)
        for source in frozenset(sources):
            available_chains.graph1.add_node(source)

        available_chains.adjust()
        return available_chains

    # scripts is a list of lists
    def _choose_by_preservance_priority(self, scripts):
        # a list of lists
        minimal_preservance_paths = shortest_lists_of_edges(scripts, lambda e: Supremum(-e['script'].base.preservance))
        # minimal_preservance_scripts = [[s['script'] for s in l if 'script' in s] for l in minimal_preservance_scripts]
        # return shortest_lists_of_edges(minimal_preservance_paths, lambda e: e['weight'])
        return shortest_lists_of_edges(minimal_preservance_paths, lambda e: e['weight'])

    def _get_ns(self, node):
        if node.namespaceURI:
            result = [URIRef(node.namespaceURI)]
        else:
            result = []
        if getattr(node, 'attributes', None) is None:
            return result
        attr_nodes = [URIRef(attr.namespaceURI) for attr in node.attributes.values() \
                      if attr.namespaceURI is not None and attr.namespaceURI != 'http://www.w3.org/2000/xmlns/']
        result.extend(sorted(set(attr_nodes)))  # set() to avoid repetitions
        return result

    def _outer_node_script(self, node):
        NSs = [frozenset([URIRef(ns)]) for ns in self._get_ns(node)]
        if not NSs:
            return None
        available_chains = self._available_chains(NSs)
        try:
            # list() to force exception if there is no path
            paths = list()
            for ns in NSs:
                paths.extend(available_chains.all_shortest_paths(ns, self.state.opts.target_namespaces, weight='weight'))
        except nx.NetworkXNoPath:
            return None
        p2 = shortest_paths_to_edges(available_chains.graph.composite_graph, paths, lambda e: e['weight'])
        return [path for path in p2 if not path[0]['script'].base.transformer.inwardness]

    # Almost duplicate code with first_child_in_target()
    def all_childs_in_target_hash(self):
        result = set()

        # use depth-first search
        stack = []
        stack.append(self.state.dom.documentElement)
        while stack:
            v = stack.pop()
            if not v.childNodes:
                for x in reversed(stack):
                    result.add(x)
                    if x.namespaceURI is None or URIRef(x.namespaceURI) not in self.state.opts.target_namespaces:
                        break
            for w in v.childNodes:
                stack.append(w)

        return result

    # Almost duplicate code with all_childs_in_target_hash()
    def first_child_in_target(self):
        # use depth-first search
        stack = [self.state.dom.documentElement]
        while stack:
            v = stack.pop()
            if not v.childNodes:
                last_result = None
                for x in reversed(stack):
                    last_result = x
                    if x.namespaceURI is None or URIRef(x.namespaceURI) not in self.state.opts.target_namespaces:
                        break
                return last_result
            for w in v.childNodes:
                if w.nodeType == w.ELEMENT_NODE:
                    stack.append(w)
