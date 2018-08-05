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

from rdflib import RDF, URIRef

from xmlboiler.core.rdf_recursive_descent.base import ParseException


def check_node_class(relation, parse_context, graph, node, klass, on_error):
    for i in graph.objects(node, RDF.type):
        if isinstance(i, URIRef) and relation.is_connected(i, klass):
            return
    str = lambda: parse_context.translate("Node {node} must be of class {klass}.").format(node=node, klass=klass)
    parse_context.throw(on_error, str)


class ClassForestParser(object):
    def __init__(self, node_parser, klass, subclasses):
        self.node_parser = node_parser
        self.klass = klass
        self.subclasses = subclasses

    def parse(self, parse_context, graph):
        result = []
        # TODO: Not the fastest algorithm
        # TODO: It does a wrong thing if one node has multiple "type" predicates
        for node, nodeClass in graph[:RDF.type]:
            if isinstance(nodeClass, URIRef) and self.subclasses.is_connected(nodeClass, self.klass):
                try:
                    result.append(self.node_parser.parse(parse_context, graph, node))
                except ParseException:
                    pass
        return result
