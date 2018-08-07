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

# the second algorithm from https://en.wikiversity.org/wiki/Automatic_transformation_of_XML_namespaces/Transformations/Automatic_transformation

from networkx import nx
from rdflib import URIRef

from xmlboiler.core.graph.path import shortest_paths_to_edges
from .next_script_base import ScriptsIteratorBase


class ScriptsIterator(ScriptsIteratorBase):
    def __next__(self):
        next_outer = self._next_outer_script()
        if next_outer:
            return next_outer

        childs_hash = self.all_childs_in_target_hash()

        elements = []
        # use depth-first search
        stack = []
        stack.append(self.state.dom.documentElement)
        while stack:
            v = stack.pop()
            if not v.childNodes:
                for x in reversed(stack):
                    if x not in childs_hash:
                        break
                    elements.append(x)
            for w in v.childNodes:
                stack.append(w)

        namespaces = frozenset([URIRef(e.namespaceURI) for e in elements if e.namespaceURI is not None])

        # Check that for this element there is a known inwardly processed script
        available_chains = self._available_chains(namespaces, self.state.opts.target_namespaces)

        paths = []
        for source in namespaces:
            try:
                nodes = nx.all_shortest_paths(available_chains.graph,
                                              frozenset([source]),
                                              self.state.opts.target_namespaces)
                paths.extend(shortest_paths_to_edges(available_chains.graph, nodes, lambda e: e['weight']))
            except nx.NetworkXNoPath:
                pass
        if not paths:
            raise StopIteration

        maximal_priority_edges = self._choose_by_preservance_priority(paths)
        if not maximal_priority_edges:
            raise StopIteration
        return maximal_priority_edges[0][0]
