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

from rdflib import RDF, BNode

from xmlboiler.core.rdf_recursive_descent.base import NodeParserWithError


class ListParser(NodeParserWithError):
    def __init__(self, subparser, error):
        super().__init__(error)
        self.subparser = subparser

    def parse(self, parse_context, graph, node):
        """
        TODO: check list validity more thoroughly
        """
        if not graph.value(node, RDF.nil) and (not isinstance(node, BNode) or not graph.value(node, RDF.first)):
            parse_context.throw(self.on_error,
                                lambda: parse_context.translate("Node {node} should be a list.").format(node=list))
        items = list(graph.items(node))  # TODO: Is list() necessary?
        return [self.subparser.parse(parse_context, graph, elt) for elt in items]