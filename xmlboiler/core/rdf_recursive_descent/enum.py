from rdflib import URIRef

from .base import *


class EnumParser(NodeParserWithError):
    def __init__(self, map, on_error):
        super(NodeParserWithError, self).__init__(on_error)
        self.map = map

    def parse(self, parse_context, graph, node):
        if node not in URIRef:
            self.throw(lambda: parse_context.translate("Node %s should be an IRI.") % str(node))
        try:
            value = self.map[node]
        except KeyError:
            self.throw(lambda: parse_context.translate("The IRI %s is unknown.") % str(node))
        return value
