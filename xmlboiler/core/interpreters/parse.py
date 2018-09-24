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

import shutil

from dependency_injector import providers, containers
from rdflib import URIRef

from xmlboiler.core import execution_context_builders
from xmlboiler.core.data import Global
from xmlboiler.core.execution_context_builders import context_for_logger, Contexts
from xmlboiler.core.packages.version_wrapper import VersionWrapper, version_wrapper_create
from xmlboiler.core.rdf_recursive_descent.base import ErrorHandler, ParseException, ParseContext
from xmlboiler.core.rdf_recursive_descent.compound import ZeroOnePredicate, Choice, Enum, OnePredicate, \
    PostProcessNodeParser
from xmlboiler.core.rdf_recursive_descent.enum import EnumParser
from xmlboiler.core.rdf_recursive_descent.list import ListParser
from xmlboiler.core.rdf_recursive_descent.literal import StringLiteral, IRILiteral
from .parse_impl import MainParser, InterpreterParseContext

PREFIX = "http://portonvictor.org/ns/trans/internal/"


class _FromPackageVersion:
    pass


class Interpeters(object):
    def __init__(self, soft_options, execution_context, graph):
        self.soft_options = soft_options
        self.graph = graph
        self.execution_context = context_for_logger(execution_context, Contexts.default_logger('interpreters-file'))

        list_node = next(graph[URIRef(PREFIX + "boiler"):URIRef(PREFIX + "interpretersList")])
        the_list = ListParser(IRILiteral(ErrorHandler.FATAL), ErrorHandler.FATAL).parse(ParseContext(execution_context), graph, list_node)
        self.order = {k: v for v, k in enumerate(the_list)}

    def check_version(self, min_version, max_version, main_node):
        result = None
        if self.soft_options.package_manager:
            result = self.check_version_by_package(min_version, max_version, main_node)
            if result:
                return result
        if self.soft_options.path:
            return self.check_version_by_executable(main_node, not self.soft_options.package_manager)
        return None

    def check_version_by_package(self, min_version, max_version, main_node):
        parse_context = ParseContext(self.execution_context)

        if min_version is None and max_version is None:  # any version is OK
            try:
                package = OnePredicate(URIRef(PREFIX + "debianPackage"), StringLiteral(ErrorHandler.FATAL), ErrorHandler.IGNORE). \
                    parse(parse_context, self.graph, main_node)
                if self.soft_options.package_manager.determine_package_version(package) is None:
                    self.warn_no_package(package, min_version, max_version)
                    return False
                return True
            except ParseException:
                return False

        if min_version is None:
            min_version = float('-inf')
        if max_version is None:
            max_version = float('inf')

        version_wrapper = version_wrapper_create(self.soft_options.package_manager)

        min_version = version_wrapper(min_version)
        max_version = version_wrapper(max_version)

        version_parser = Choice([PostProcessNodeParser(StringLiteral(ErrorHandler.IGNORE), version_wrapper),
                                 EnumParser({PREFIX + 'fromPackageVersion': _FromPackageVersion()})])
        lang_min_version = ZeroOnePredicate(URIRef(PREFIX + "langMinVersion"), version_parser, ErrorHandler.FATAL). \
            parse(parse_context, self.graph, main_node)
        lang_max_version = ZeroOnePredicate(URIRef(PREFIX + "langMaxVersion"), version_parser, ErrorHandler.FATAL). \
            parse(parse_context, self.graph, main_node)
        lang_min_version = lang_min_version or version_wrapper(float('-inf'))
        lang_max_version = lang_max_version or version_wrapper(float('inf'))

        # First try to check without retrieving package version (for efficiency)
        if not isinstance(lang_min_version, _FromPackageVersion) and max_version < lang_min_version:
            return False
        if not isinstance(lang_max_version, _FromPackageVersion) and min_version > lang_max_version:
            return False

        pmin_version = ZeroOnePredicate(URIRef(PREFIX + "packageMinVersion"), StringLiteral(ErrorHandler.FATAL), ErrorHandler.FATAL). \
            parse(parse_context, self.graph, main_node)
        pmax_version = ZeroOnePredicate(URIRef(PREFIX + "packageMaxVersion"), StringLiteral(ErrorHandler.FATAL), ErrorHandler.FATAL). \
            parse(parse_context, self.graph, main_node)
        if lang_min_version is _FromPackageVersion or lang_max_version is _FromPackageVersion or \
                pmin_version is not None or pmax_version is not None:
            try:
                package = OnePredicate(URIRef(PREFIX + "debianPackage"), StringLiteral(ErrorHandler.FATAL), ErrorHandler.IGNORE). \
                    parse(parse_context, self.graph, main_node)
            except ParseException:
                return False
            real_version = self.soft_options.package_manager.determine_package_version(package)
            if real_version is None:  # no such Debian package
                self.warn_no_package(package, min_version, max_version)
                return False
            if lang_min_version is _FromPackageVersion:
                if VersionWrapper(real_version) > max_version:
                    self.warn_no_package(package, min_version, max_version)
                    return False
            if lang_max_version is _FromPackageVersion:
                if VersionWrapper(real_version) < min_version:
                    self.warn_no_package(package, min_version, max_version)
                    return False
            if (pmin_version is not None and VersionWrapper(real_version) < VersionWrapper(pmin_version)) or \
                    (pmax_version is not None and VersionWrapper(real_version) > VersionWrapper(pmax_version)):
                self.warn_no_package(package, min_version, max_version)
                return False
        return True

    def check_version_by_executable(self, main_node, warn):
        parse_context = ParseContext(self.execution_context)
        executable = ZeroOnePredicate(URIRef(PREFIX + "executable"), StringLiteral(ErrorHandler.FATAL), ErrorHandler.FATAL). \
            parse(parse_context, self.graph, main_node)
        if executable is None:
            return False
        if shutil.which(executable) is not None:
            return True
        if warn:
            msg = self.execution_context.translations.gettext(
                "Trying to use not installed executable {e}.").format(e=executable)
            self.execution_context.logger.warn(msg)
        return False

    # TODO: Cache the results
    # TODO: Allow to use the URI of the interpreter directly instead of the language name
    def find_interpreter(self, language, min_version, max_version):
        """
        :param language: the URI of the language
        :param version: string or None
        """
        main_nodes = list(self.graph.subjects(URIRef(PREFIX + "lang"), language))
        main_nodes = sorted(main_nodes, key=lambda u: self.order[u])
        for main_node in main_nodes:
            if self.check_version(min_version, max_version, main_node):
                return main_node
        return None

    # TODO: Cache the results
    # script_url is the URL of the executable (however it may be instead a local file)
    def construct_command_line(self, node, script_str, params, inline=False):
        """
        :param node:
        :param script_str:
        :param params: script params, a list of 2-tuples
        :param inline: use inline script, not scriptURL
        :return: a list of strings
        """
        parse_context = InterpreterParseContext(self.execution_context, script_str, params)
        pred = URIRef(PREFIX + ('inlineCommand' if inline else 'scriptCommand'))
        parser = ZeroOnePredicate(pred, MainParser(), ErrorHandler.FATAL)
        return parser.parse(parse_context, self.graph, node)

    def warn_no_package(self, package, min_version, max_version):
        min = min_version if min_version is not None else '*'
        max = max_version if max_version is not None else '*'
        msg = self.execution_context.translations.gettext(
            "Trying to use not installed package {p} (versions {min} - {max}).").format(p=package, min=min, max=max)
        self.execution_context.logger.warn(msg)

# TODO: Use proper dependency injection instead of the singleton
class Providers(containers.DeclarativeContainer):
    interpreters_factory = providers.ThreadLocalSingleton(Interpeters,
                                                          execution_context=execution_context_builders.Contexts.execution_context,
                                                          graph=Global.load_rdf('core/data/interpreters.ttl'))
