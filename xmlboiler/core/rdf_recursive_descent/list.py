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

from rdflib.collection import Collection

from xmlboiler.core.rdf_recursive_descent.base import NodeParserWithError


class ListParser(NodeParserWithError):
    def __init__(self, subparser):
        self.subparser = subparser

    def parse(self, parse_context, graph, node):
        """
        TODO: check list validity
        """
        items = graph.items(node)
        return [self.subparser.parse(parse_context, graph, elt) for elt in items]