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

from abc import abstractmethod, ABC
from dependency_injector import providers
from enum import Enum, auto

from xmlboiler.core.execution_context_builders import Contexts


class BaseParseException(Exception):
    """
    Some people say that exceptions for control flow are bad. Some disagree.

    Victor Porton finds that doing this without exceptions is somehow cumbersome and may be error-prone.
    """
    pass


class ParseException(BaseParseException):
    pass


class FatalParseException(BaseParseException):
    pass


class ErrorHandler(Enum):
    """
    TODO: rename?
    """
    IGNORE  = auto()
    WARNING = auto()
    FATAL   = auto()


class ParseContext(object):
    def __init__(self, execution_context):
        self.execution_context = execution_context

    def throw(self, handler: ErrorHandler, str):
        if handler == ErrorHandler.IGNORE:
            raise ParseException()
        elif handler == ErrorHandler.WARNING:
            if callable(str):
                str = str()
            self.execution_context.logger.warning(str)
            raise ParseException(str)
        elif handler == ErrorHandler.FATAL:
            if callable(str):
                str = str()
            self.execution_context.logger.error(str)
            raise FatalParseException(str)

    # to shorten code
    def translate(self, str):
        return self.execution_context.translations.gettext(str)

class NodeParser(ABC):
    """
    Parses a node of RDF resource (and its "subnodes").

    Usually NodeParser and Predicate parser call each other (as in mutual recursion)

    WARNING: Don't use this parser to parse recursive data structures,
    because it may lead to infinite recursion on circular RDF.

    TODO: Make parse_context a constructor argument instead (here and in PredicateParser)
    """

    @abstractmethod
    def parse(self, parse_context, graph, node):
        pass


class PredicateParser(ABC):
    """
    Parses a given predicate (which may participate in several relationships)
    of a given RDF node.

    Usually NodeParser and Predicate parser call each other (as in mutual recursion)
    """

    def __init__(self, predicate):
        self.predicate = predicate

    @abstractmethod
    def parse(self, parse_context, graph, node):
        pass


class NodeParserWithError(NodeParser):
    def __init__(self, on_error):
        super().__init__()
        self.on_error = on_error


class PredicateParserWithError(PredicateParser):
    def __init__(self, predicate, on_error):
        super().__init__(predicate)
        self.on_error = on_error


default_parse_context = providers.Factory(ParseContext, execution_context=Contexts.execution_context)