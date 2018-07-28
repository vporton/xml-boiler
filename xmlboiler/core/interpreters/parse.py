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
from rdflib import URIRef

from xmlboiler.core import execution_context_builders
from xmlboiler.core.data import Global
from xmlboiler.core.packages.base import ThePackageManaging
from xmlboiler.core.packages.version_wrapper import VersionWrapper
from xmlboiler.core.rdf_recursive_descent.base import ErrorHandler, ParseException, ParseContext
from xmlboiler.core.rdf_recursive_descent.compound import ZeroOnePredicate, Choice, Enum, OnePredicate, \
    PostProcessPredicateParser
from xmlboiler.core.rdf_recursive_descent.list import ListParser
from xmlboiler.core.rdf_recursive_descent.literal import StringLiteral
from .parse_impl import MainParser, InterpreterParseContext

PREFIX = "http://portonvictor.org/ns/trans/internal/"

_Version = ThePackageManaging.VersionClass


class _FromPackageVersion:
    pass


class Interpeters(object):
    def __init__(self, execution_context, graph):
        self.graph = graph
        self.execution_context = execution_context

        list_node = graph[:URIRef(PREFIX + "interpretersList")][0]
        the_list = ListParser(ErrorHandler.FATAL).parse(ParseContext(execution_context), graph, list_node)
        self.order = {k: v for v, k in enumerate(the_list)}

    def check_version(self, min_version, max_version, main_node):
        if min_version is None and max_version is None:  # any version is OK
            return True

        if min_version is None:
            min_version = float('-inf')
        if max_version is None:
            max_version = float('inf')

        min_version = VersionWrapper(min_version)
        max_version = VersionWrapper(max_version)

        parse_context = ParseContext(self.execution_context)
        version_parser = Choice([PostProcessPredicateParser(StringLiteral(), VersionWrapper),
                                 Enum({PREFIX + ':fromPackageVersion': _FromPackageVersion()})])
        lang_min_version = ZeroOnePredicate(PREFIX + "langMinVersion", version_parser, ErrorHandler.FATAL). \
            parse(parse_context, self.graph, main_node)
        lang_max_version = ZeroOnePredicate(PREFIX + "langMaxVersion", version_parser, ErrorHandler.FATAL). \
            parse(parse_context, self.graph, main_node)
        lang_min_version = lang_min_version or VersionWrapper(float('-inf'))
        lang_max_version = lang_max_version or VersionWrapper(float('inf'))

        # First try to check without retrieving package version (for efficiency)
        if not isinstance(lang_min_version, _FromPackageVersion) and max_version < lang_min_version:
            return False
        if not isinstance(lang_max_version, _FromPackageVersion) and min_version > lang_max_version:
            return False

        pmin_version = ZeroOnePredicate(PREFIX + "packageMinVersion", StringLiteral(), ErrorHandler.FATAL). \
            parse(parse_context, self.graph, main_node)
        pmax_version = ZeroOnePredicate(PREFIX + "packageMaxVersion", StringLiteral(), ErrorHandler.FATAL). \
            parse(parse_context, self.graph, main_node)
        if lang_min_version is _FromPackageVersion or lang_max_version is _FromPackageVersion or \
                pmin_version is not None or pmax_version is not None:
            try:
                package = OnePredicate(StringLiteral(), ErrorHandler.IGNORE)
            except ParseException:
                return False
            real_version = ThePackageManaging.determine_package_version(package)
            if real_version is None:  # no such Debian package
                return False
            if lang_min_version is _FromPackageVersion:
                if VersionWrapper(real_version) > max_version:
                    return False
            if lang_max_version is _FromPackageVersion:
                if VersionWrapper(real_version) < min_version:
                    return False
            if (pmin_version is not None and VersionWrapper(real_version) < VersionWrapper(pmin_version)) or \
                    (pmax_version is not None and VersionWrapper(real_version) > VersionWrapper(pmax_version)):
                return False
        return True

    # TODO: Cache the results
    # TODO: Allow to use the URI of the interpreter directly instead of the language name
    # FIXME: We have two version ranges: for the interpreter and for the script, not a range and a version as here
    def find_interpreter(self, language, min_version, max_version):
        """
        :param language: the URI of the language
        :param version: string or None
        """
        main_nodes = list(self.graph.subjects(PREFIX + "lang", language))
        main_nodes = sorted(main_nodes, lambda u: self.order[u])
        for main_node in main_nodes:
            if self.check_version(min_version, max_version, main_node):
                return main_node

    # TODO: Cache the results
    # script_url is the URL of the executable (however it may be instead a local file)
    def construct_command_line(self, node, script_url, params):
        """
        :param node:
        :param script_url:
        :param params: script params, a list of 2-tuples
        :return: a list of strings
        """
        parse_context = InterpreterParseContext(self.execution_context, script_url, params)
        parser = OnePredicate(URIRef(PREFIX + 'command'), MainParser(), ErrorHandler.FATAL)
        return parser.parse(parse_context, self.graph, node)

# TODO: Use proper dependency injection instead of the singleton
interpreters = providers.ThreadLocalSingleton(Interpeters,
                                              execution_context=execution_context_builders.Contexts.default_context,
                                              graph=Global.load_rdf('interpreters.ttl'))
