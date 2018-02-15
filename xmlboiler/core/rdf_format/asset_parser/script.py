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

from xmlboiler.core.rdf_format.base import MAIN_NAMESPACE
from xmlboiler.core.rdf_recursive_descent.base import NodeParser
from xmlboiler.core.rdf_recursive_descent.compound import Choice
from xmlboiler.core.rdf_recursive_descent.enum import EnumParser
from xmlboiler.core.rdf_format.asset import AssetInfo, TransformerKindEnum


class ScriptInfoParser(Choice):
    def __init__(self, subclasses, script_kind: AssetInfo.ScriptKindEnum):
        # Intentionally not using dependency injection pattern
        super(Choice, self).__init__([CommandScriptInfoParser(subclasses, script_kind),
                                      WebServiceScriptInfoParser(subclasses, script_kind)])
        # self.subclasses = subclasses
        # self.script_kind = script_kind

    # def parse(self, parse_context, graph, node):

class BaseScriptInfoParser(NodeParser):
    def __init__(self, script_kind):
        self.script_kind = script_kind

    # FIXME: Race conditions when multithreading!
    _transformer_kind_parser = None
    _validator_kind_parser   = None

    @staticmethod
    def transformer_kind_parser():
        if BaseScriptInfoParser._transformer_kind_parser is not None:
            return BaseScriptInfoParser._transformer_kind_parser
        map = {MAIN_NAMESPACE + "entire": TransformerKindEnum.ENTIRE,
               MAIN_NAMESPACE + "sequential": TransformerKindEnum.SEQUENTIAL,
               MAIN_NAMESPACE + "upDown": TransformerKindEnum.UP_DOWN,
               MAIN_NAMESPACE + "downUp": TransformerKindEnum.DOWN_UP}
        BaseScriptInfoParser._transformer_kind_parser = EnumParser(map)
        return BaseScriptInfoParser._transformer_kind_parser

    # TODO

# TODO
class CommandScriptInfoParser(NodeParser):
    pass

# TODO
class WebServiceScriptInfoParser(NodeParser):
    pass