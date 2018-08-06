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

from rdflib import URIRef

from xmlboiler.core.rdf_format.asset import Transformer, ScriptKindEnum
from xmlboiler.core.rdf_format.asset_parser.script import ScriptInfoParser
from xmlboiler.core.rdf_format.base import MAIN_NAMESPACE
from xmlboiler.core.rdf_recursive_descent.base import NodeParser, ErrorHandler
from xmlboiler.core.rdf_recursive_descent.compound import OneOrMorePredicate, OnePredicate, ZeroOnePredicate, \
    ZeroOrMorePredicate
from xmlboiler.core.rdf_recursive_descent.literal import IRILiteral, BooleanLiteral
from xmlboiler.core.rdf_recursive_descent.types import check_node_class


class TransformerParser(NodeParser):
    def __init__(self, subclasses):
        self.subclasses = subclasses

    def parse(self, parse_context, graph, node):
        klass = URIRef(MAIN_NAMESPACE + "Transformer")
        check_node_class(self.subclasses, parse_context, graph, node, klass, ErrorHandler.IGNORE)

        result = Transformer()

        source_namespaces_parser = OneOrMorePredicate(URIRef(MAIN_NAMESPACE + "sourceNamespace"),
                                                      IRILiteral(ErrorHandler.WARNING),
                                                      ErrorHandler.WARNING)
        result.source_namespaces = source_namespaces_parser.parse(parse_context, graph, node)
        target_namespaces_parser = ZeroOrMorePredicate(URIRef(MAIN_NAMESPACE + "targetNamespace"),
                                                       IRILiteral(ErrorHandler.WARNING))
        result.target_namespaces = target_namespaces_parser.parse(parse_context, graph, node)

        precedence_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "precedence"),
                                             IRILiteral(ErrorHandler.WARNING),
                                             ErrorHandler.WARNING)
        result.precedence = precedence_parser.parse(parse_context, graph, node)
        inwardness_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "inward"),
                                             BooleanLiteral(ErrorHandler.WARNING),
                                             ErrorHandler.WARNING,
                                             True)
        result.inwardness = inwardness_parser.parse(parse_context, graph, node)
        ignore_target_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "ignoreTarget"),
                                                BooleanLiteral(ErrorHandler.WARNING),
                                                ErrorHandler.WARNING)
        result.ignore_target = ignore_target_parser.parse(parse_context, graph, node)
        universal_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "universal"),
                                            BooleanLiteral(ErrorHandler.WARNING),
                                            ErrorHandler.WARNING)
        result.universal = universal_parser.parse(parse_context, graph, node)

        script_node_parser = ScriptInfoParser(result, self.subclasses, ScriptKindEnum.TRANSFORMER)
        script_parser = OneOrMorePredicate(URIRef((MAIN_NAMESPACE + "script")), script_node_parser, ErrorHandler.WARNING)
        result.scripts = script_parser.parse(parse_context, graph, node)

        return result