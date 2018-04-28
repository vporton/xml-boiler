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

import networkx as nx

from xmlboiler.core.alg.path import GraphOfScripts


class ScriptsIterator(object):
    def __init__(self, state):
        self.state = state

    def __iter__(self):
        return self

    def __next__(self):
        self.available_chains = GraphOfScripts(self.state.scripts)  # inefficient?
        first_edges = []
        for source in self.state.all_namespaces:
            for target in self.state.opts.targetNamespaces:  # FIXME: Check for the right var
                # FIXME: Does not work with universal edges
                edges = self.available_chains.first_edges_for_shortest_path(self, source, target)
                first_edges.extend(edges)
        if not first_edges:
            raise StopIteration
        executed = GraphOfScripts(self.state.executed_scripts)
        if self.check_has_executed(executed):
            self.available_chains = executed
            first_edges2 = []
            for source in self.state.all_namespaces:
                for target in self.state.opts.targetNamespaces:  # FIXME: Check for the right var
                    # FIXME: Does not work with universal edges
                    edges = executed.first_edges_for_shortest_path(self, source, target)
                    first_edges2.extend(edges)
            if len(first_edges2) > 1:
                # TODO: Option to make it fatal
                self.state.execution_context.warning("More than one possible executed scripts.")
        # TODO

    def check_has_executed(self, executed):
        for source in self.state.all_namespaces:
            for target in self.state.opts.targetNamespaces:  # FIXME: Check for the right var
                if nx.has_path(executed, source, target):
                    return True
        return False