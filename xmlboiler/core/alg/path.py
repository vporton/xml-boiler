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


class Search(object):
    def __init__(self, enriched_scripts):
        self.graph = nx.MultiDiGraph()
        for scr in enriched_scripts:
            source = frozenset(scr.transfomer.source_namespaces)
            target = frozenset(scr.transfomer.target_namespaces)
            # TODO: There are two proposed formulas for weight in the specification
            weight = 1 / (scr.script.base.preservance + scr.script.base.stability + scr.script.base.preference)
            self.graph.add_node(source, target, script=scr, weight=weight)
        # TODO: The below is inefficient
        for i in self.graph.nodes:
            for j in self.graph.nodes:
                if i <= j:
                    self.graph.add_node(i, j, weight=0)

    def first_edges_for_shortest_path(self, source, target):
        paths = nx.all_shortest_paths(self.graph, source, target, weight='weight')
        edges = []
        for path in paths:
            # TODO: remove zero-weight interset nodes
            pass  # FIXME
        # TODO