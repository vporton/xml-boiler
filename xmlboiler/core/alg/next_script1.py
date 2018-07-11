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

from xmlboiler.core.graph.minmax import Supremum
from xmlboiler.core.graph.path import shortest_lists_of_edges
from .next_script_base import ScriptsIteratorBase


def _precedence(edge):
    return edge['script'].transformer.precedence

class ScriptsIterator(ScriptsIteratorBase):
    def __next__(self):
        available_chains = self._available_chains(self.state.all_namespaces)
        first_edges = []
        for source in self.state.all_namespaces:
            # FIXME: Does not work with universal edges
            # FIXME: Should first filter out the non-executed scripts
            edges = available_chains.first_edges_for_shortest_path(self, frozenset([source]), self.state.opts.targetNamespaces)
            first_edges.extend(edges)
        if not first_edges:
            raise StopIteration

        first_edges = filter(lambda e: _precedence(e) is not None, first_edges)
        first_edges = self._checked_scripts(first_edges)

        # Choose the script among first_edges with highest precedence
        highest_precedences = self.state.graph.maxima(first_edges, key=lambda e: _precedence(e))
        if len(highest_precedences) != 1:  # don't know how to choose
            raise StopIteration
        highest_precedence = highest_precedences[0]
        highest_precedence_scripts = filter(lambda e: _precedence(e) == highest_precedence, first_edges)
        if len(highest_precedence_scripts) == 1:
            return highest_precedence_scripts[0]  # TODO: Add it to the list of executed scripts

        if highest_precedence not in self.state.singletons:
            raise StopIteration

        # There are several highest_precedence_scripts - choose the maximal preservance and maximal priority
        # a list of lists
        minimal_preservance_paths = shortest_lists_of_edges(highest_precedence_scripts,
                                                            lambda e: Supremum(-e['script'].base.preservance))
        # minimal_preservance_scripts = [[s['script'] for s in l if 'script' in s] for l in minimal_preservance_scripts]
        maximal_priority_edges = shortest_lists_of_edges(minimal_preservance_paths, lambda e: e['weight'])

        if not maximal_priority_edges:
            raise StopIteration
        return maximal_priority_edges[0][0]  # TODO: Add it to the list of executed scripts
