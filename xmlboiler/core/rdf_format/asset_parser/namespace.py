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

from xmlboiler.core.rdf_format.asset import Namespace, ScriptKindEnum
from xmlboiler.core.rdf_format.asset_parser.script import ScriptInfoParser
from xmlboiler.core.rdf_format.base import MAIN_NAMESPACE
from xmlboiler.core.rdf_recursive_descent.base import NodeParser, ErrorHandler
from xmlboiler.core.rdf_recursive_descent.compound import OneOrMorePredicate
from xmlboiler.core.rdf_recursive_descent.types import check_node_class


class NSParser(NodeParser):
    def __init__(self, subclasses):
        self.subclasses = subclasses

    def parse(self, parse_context, graph, node):
        klass = URIRef(MAIN_NAMESPACE + "Namespace")
        check_node_class(self.subclasses, parse_context, graph, node, klass, ErrorHandler.IGNORE)

        result = Namespace(resource=node)

        script_node_parser = ScriptInfoParser(result, self.subclasses, ScriptKindEnum.VALIDATOR)
        script_parser = OneOrMorePredicate(URIRef(MAIN_NAMESPACE + "validator"), script_node_parser, ErrorHandler.WARNING)
        result.validators = script_parser.parse(parse_context, graph, node)

        return result