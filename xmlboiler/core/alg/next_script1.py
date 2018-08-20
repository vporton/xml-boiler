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

# the first algorithm from https://en.wikiversity.org/wiki/Automatic_transformation_of_XML_namespaces/Transformations/Automatic_transformation

import networkx as nx

from xmlboiler.core.graph.path import shortest_paths_to_edges
from .next_script_base import ScriptsIteratorBase


def _precedence(edge):
    return edge['script'].transformer.precedence

class ScriptsIterator(ScriptsIteratorBase):
    def __next__(self):
        available_chains = self._available_chains(self.state.all_namespaces)

        paths = []
        for source in self.state.all_namespaces:
            try:
                nodes = available_chains.all_shortest_paths(frozenset([source]),
                                                            self.state.opts.target_namespaces,
                                                            weight='weight')
                paths.extend(shortest_paths_to_edges(available_chains.graph.composite_graph, nodes,
                                                     lambda e: e['weight']))
            except nx.NetworkXNoPath:
                pass
        if not paths:
            raise StopIteration

        paths = filter(lambda e: _precedence(e[0]) is not None, paths)

        # Choose the script among first_edges with highest precedence
        highest_precedences = self.state.precedences_higher.maxima(paths, key=lambda e: _precedence(e[0]))
        if len(highest_precedences) != 1:  # don't know how to choose
            raise StopIteration
        highest_precedence = highest_precedences[0]
        highest_precedence_scripts = filter(lambda e: _precedence(e[0]) == highest_precedence, paths)
        if len(highest_precedence_scripts) == 1:
            return highest_precedence_scripts[0]

        if highest_precedence not in self.state.singletons:
            raise StopIteration

        maximal_priority_edges = self._choose_by_preservance_priority(highest_precedence_scripts)

        if not maximal_priority_edges:
            raise StopIteration
        return maximal_priority_edges[0][0]
