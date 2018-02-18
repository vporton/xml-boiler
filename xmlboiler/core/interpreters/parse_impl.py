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

from xmlboiler.core.rdf_recursive_descent.base import ParseContext, NodeParser


class InterpreterParseContext(ParseContext):
    def __init__(self, execution_context, script_url, params):
        super(ParseContext, self).__init__(execution_context)
        self.script_url = script_url
        self.params = params


class ArgumentListParser(NodeParser):
    def parse(self, parse_context, graph, node):
        TODO
