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
from dependency_injector import providers

from rdflib import URIRef, RDF, RDFS

from xmlboiler.core.rdf_base.subclass import SubclassRelationForType, SubclassContainers
from xmlboiler.core.rdf_format.asset_parser.namespace import NSParser
from xmlboiler.core.rdf_format.base import MAIN_NAMESPACE
from xmlboiler.core.rdf_format.asset import AssetInfo
from xmlboiler.core.rdf_format.asset_parser.transformer import TransformerParser
from xmlboiler.core.rdf_recursive_descent.base import ErrorHandler, default_parse_context
from xmlboiler.core.rdf_recursive_descent.list import ListParser
from xmlboiler.core.rdf_recursive_descent.literal import IRILiteral
from xmlboiler.core.rdf_recursive_descent.types import ClassForestParser


class AssetParser(object):
    def __init__(self, parse_context, subclasses):
        self.parse_context = parse_context
        self.subclasses = subclasses

    def parse(self, graph):
        result = AssetInfo()

        transformerParser = ClassForestParser(
            TransformerParser(self.subclasses), URIRef(MAIN_NAMESPACE + "Transformer"), self.subclasses);
        result.transformers = transformerParser.parse(self.parse_context, graph)
        nsParser = ClassForestParser(
            NSParser(self.subclasses), URIRef(MAIN_NAMESPACE + "Namespace"), self.subclasses)
        result.namespaces = nsParser.parse(self.parse_context, graph)

        result.see_also_transform = self.scan_see_also(graph, MAIN_NAMESPACE + "transform")
        result.see_also_validate  = self.scan_see_also(graph, MAIN_NAMESPACE + "validate")

        result.precedences_subclasses = SubclassRelationForType(URIRef(MAIN_NAMESPACE + "Precedence"),
                                                                context=self.parse_context.execution_context,
                                                                graph=graph,
                                                                relation=RDFS.subClassOf)
        result.precedences_higher = SubclassRelationForType(URIRef(MAIN_NAMESPACE + "Precedence"),
                                                            context=self.parse_context.execution_context,
                                                            graph=graph,
                                                            relation=URIRef(MAIN_NAMESPACE + "higherThan"))

        return result

    def scan_see_also(self, graph, kind_URI):
        nodes = list(graph[:RDFS.seeAlso])
        # Can be simplified using OnePredicate class
        if len(nodes) == 0:
            return []
        if len(nodes) > 1:
            # TODO: Show URL of the asset
            msg = self.parse_context.translate("Multiple rdfs:seeAlso in asset") #.format()
            self.parse_context.throw(ErrorHandler.FATAL, msg)
        return ListParser(IRILiteral(ErrorHandler.WARNING)).parse(self.parse_context, graph, nodes[0])


asset_parser_provider = providers.Factory(AssetParser,
                                          parse_context=default_parse_context,
                                          subclasses=SubclassContainers.basic_subclasses)
