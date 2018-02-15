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

        script_node_parser = ScriptInfoParser(self.subclasses, ScriptKindEnum.VALIDATOR)
        script_parser = OneOrMorePredicate(URIRef(MAIN_NAMESPACE + "validator"), script_node_parser, ErrorHandler.WARNING)
        validators = script_parser.parse(parse_context, graph, node)

        return Namespace(resource=node, validators=validators)
