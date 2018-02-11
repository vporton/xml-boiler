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

from xmlboiler.core.rdf_recursive_descent.base import *


class Choice(NodeParser):
    """
    TODO: If the node conforms to more than one choice, this class does
    not conform to the specification.
    """

    def __init__(self, choices):
        self.choices = choices

    def parse(self, parse_context, graph, node):
        for p in self.choices:
            try:
                return p.parse(parse_context, graph, node)
            except ParseException:
                pass


class ZeroOrMorePredicate(PredicateParser):
    def __init__(self, predicate, child):
        super(PredicateParserWithError, self).__init__(predicate, on_error)
        self.child = child

    def parse(self, parse_context, graph, node):
        iter = graph.objects(node, self.predicate)
        return [self.child.parse(parse_context, graph, elt) for elt in iter]


class OneOrMorePredicate(PredicateParserWithError):
    def __init__(self, predicate, child, on_error):
        super(PredicateParserWithError, self).__init__(predicate, on_error)
        self.child = child

    def parse(self, parse_context, graph, node):
        parent = ZeroOrMorePredicate(self.predicate, self.child)
        value = parent.parse(parse_context, graph, node)
        if len(value) == 0:
            self.throw(self.parse_context.translate("Must have at least one predicate {pred} for node {node}.")
                       .format(pred=self.predicate, node=node))
        return value
