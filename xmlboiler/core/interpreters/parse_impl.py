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

from xmlboiler.core.rdf_recursive_descent.base import ParseContext, NodeParser, ErrorHandler
from xmlboiler.core.rdf_recursive_descent.compound import Choice, OnePredicate
from xmlboiler.core.rdf_recursive_descent.enum import EnumParser
from xmlboiler.core.rdf_recursive_descent.list import ListParser
from xmlboiler.core.rdf_recursive_descent.literal import StringLiteral

PREFIX = "http://portonvictor.org/ns/trans/internal/"


class InterpreterParseContext(ParseContext):
    def __init__(self, execution_context, script_url, params):
        super(ParseContext, self).__init__(execution_context)
        self.script_url = script_url
        self.params = params
        self.current_param = None


class MainParser(Choice):
    def __init__(self):
        """
        Every of these parsers returns a list (probably one-element) of strings.
        """
        super(Choice, self).__init__([ArgumentLiteralParser(),
                                      ArgumentListParser(),
                                      ConcatParser(),
                                      ConstantParser()])


class ArgumentLiteralParser(NodeParser):
    def parse(self, parse_context, graph, node):
        return [StringLiteral().parse(parse_context, graph, node)]

class ArgumentListParser(NodeParser):
    def parse(self, parse_context, graph, node):
        l = ListParser(MainParser()).parse(parse_context, graph, node)
        return [item for sublist in l for item in sublist]  # flatten the list


class ConcatParser(NodeParser):
    def parse(self, parse_context, graph, node):
        sub_parser = OnePredicate(PREFIX + ':concat', MainParser(), ErrorHandler.IGNORE)
        return ''.join(sub_parser.parse(parse_context, graph, node))


class ConstantParser(NodeParser):
    def parse(self, parse_context, graph, node):
        sub_parser = EnumParser({PREFIX + ':script': parse_context.script_url,
                                 PREFIX + ':name'  : parse_context.current_param.get(0),
                                 PREFIX + ':value' : parse_context.current_param.get(1)})
        return [sub_parser.parse(parse_context, graph, node)]


class ParamsParser(NodeParser):
    def parse(self, parse_context, graph, node):
        sub_parser = OnePredicate(PREFIX + ':params', MainParser(), ErrorHandler.IGNORE)
        try:
            for i in self.params:
                self.current_param = i
                l = sub_parser.parse(parse_context, graph, node)
        finally:
            self.current_param = None  # cleanup after ourselves