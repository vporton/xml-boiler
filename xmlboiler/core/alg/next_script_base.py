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


class ScriptsIteratorBase(ABC):
    def __init__(self, state):
        self.state = state

    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self):
        pass

    def _checked_scripts(self, scripts):
        # TODO: Make state.executed_scripts a set?
        if frozenset(self.state.executed_scripts).isdisjoint(scripts):
            return scripts
        return frozenset(self.state.executed_scripts).intersection(scripts)

    def _available_chains(self, sources, destinations):
        # TODO: inefficient? should hold the graph, not re-create it
        available_chains = GraphOfScripts(None, destinations, self.state.universal_precedence, self.state.precedences_higher)
        available_chains.add_scripts(self.state.scripts)
        available_chains.graph.add_node(self.state.opts.targetNamespaces)
        for source in sources:
            available_chains.graph.add_node(frozenset([source]))
        available_chains.adjust()
        return available_chains
