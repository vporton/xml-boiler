#  Copyright (c) 2017 Victor Porton,
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
