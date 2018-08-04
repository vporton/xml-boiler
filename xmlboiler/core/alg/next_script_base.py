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

from xmlboiler.core.alg.path import GraphOfScripts
from xmlboiler.core.graph.minmax import Supremum
from xmlboiler.core.graph.path import shortest_lists_of_edges


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
            for w in v.childNodes:
                scripts = self._outer_node_script(w)  # FIXME: It is a container of multiple scripts!
                if scripts:
                    return self._choose_by_preservance_priority(scripts)
                parents.append(w)
        return None

    def _checked_scripts(self, scripts):
        if self.state.executed_scripts.isdisjoint(scripts):
            return scripts
        return self.state.executed_scripts.intersection(scripts)

    def _available_chains(self, sources, destinations):
        # TODO: inefficient? should hold the graph, not re-create it
        available_chains = GraphOfScripts(None, destinations, self.state.opts.universal_precedence, self.state.precedences_higher)
        available_chains.add_scripts(self.state.scripts)
        available_chains.graph.add_node(self.state.opts.target_namespaces)
        for source in sources:
            available_chains.graph.add_node(frozenset([source]))
        available_chains.adjust()
        return available_chains

    def _choose_by_preservance_priority(self, scripts):
        # a list of lists
        minimal_preservance_paths = shortest_lists_of_edges(scripts,
                                                            lambda e: Supremum(-e['script'].base.preservance))
        # minimal_preservance_scripts = [[s['script'] for s in l if 'script' in s] for l in minimal_preservance_scripts]
        return shortest_lists_of_edges(minimal_preservance_paths, lambda e: e['weight'])

    def _get_ns(self, node):
        if node.namespaceURI:
            result = [node.namespaceURI]
        else:
            result = []
        if getattr(node, 'attributes', None) is None:
            return None
        attr_nodes = [attr for attr in node.attributes.values() if attr.namespaceURI is not None]
        result.extend(sorted(set(attr_nodes)))  # set() to avoid repetitions
        return result

    def _outer_node_script(self, node):
        NSs = self._get_ns(node)  # TODO: May be inefficient to consider all these namespaces
        if not NSs:
            return None
        scripts = []
        for s in self.state.scripts:
            if NSs[0] in s.transformer.source_namespaces:
                scripts.append(s)
        return self._checked_scripts(scripts)

    def all_childs_in_taget_hash(self):
        result = set()

        # use depth-first search
        stack = []
        stack.append(self.state.dom.documentElement)
        while stack:
            v = stack.pop()
            if not v.childNodes:
                for x in reversed(stack):
                    if x.namespaceURI not in self.state.opts.target_namespaces:
                        break
                    result.add(x)  # FIXME: What's about parents/childs?
            for w in v.childNodes:
                stack.append(w)

        return result