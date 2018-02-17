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

from rdflib import URIRef

from xmlboiler.core.packages.base import ThePackageManaging
from xmlboiler.core.rdf_recursive_descent.base import ErrorHandler, ParseException
from xmlboiler.core.rdf_recursive_descent.compound import ZeroOnePredicate, Choice, Enum, OnePredicate
from xmlboiler.core.rdf_recursive_descent.list import ListParser
from xmlboiler.core.rdf_recursive_descent.literal import StringLiteral

PREFIX = "http://portonvictor.org/ns/trans/internal/"

_Version = ThePackageManaging.VersionClass


class _FromPackageVersion:
    pass


class Interpeters(object):
    def __init__(self, graph, parse_context):
        self.graph = graph
        self.parse_context = parse_context

        list_node = graph[:URIRef("http://portonvictor.org/ns/trans/internal/interpretersList")][0]
        the_list = ListParser(ErrorHandler.FATAL).parse(parse_context, graph, list_node)
        self.order = {k: v for v, k in enumerate(the_list)}

    def check_version(self, version, main_node):
        if version is None:  # any version is OK
            return True
        version_parser = Choice([StringLiteral(), Enum({PREFIX + ':fromPackageVersion': _FromPackageVersion()})])
        lang_min_version = ZeroOnePredicate(PREFIX + "langMinVersion", version_parser, ErrorHandler.FATAL). \
            parse(self.parse_context, self.graph, main_node)
        lang_max_version = ZeroOnePredicate(PREFIX + "langMaxVersion", version_parser, ErrorHandler.FATAL). \
            parse(self.parse_context, self.graph, main_node)
        if lang_min_version is str and _Version(version) < _Version(lang_min_version):
            return False
        if lang_max_version is str:  # "X.*" at the end of version: https://en.wikiversity.org/wiki/Automatic_transformation_of_XML_namespaces/RDF_resource_format
            if lang_max_version[-2:] == '.*':
                if _Version(version) > _Version(lang_max_version[:-2]) and \
                        not version.startswith(lang_max_version[:-2] + '.'):
                    return False
            elif _Version(version) > _Version(lang_max_version):
                return False
        if lang_min_version is _FromPackageVersion or lang_max_version is _FromPackageVersion:
            try:
                package = OnePredicate(StringLiteral(), ErrorHandler.IGNORE)
            except ParseException:  # no such Debian package
                return False
            pver = ThePackageManaging.determine_package_version(package)
            if lang_min_version is _FromPackageVersion:
                if _Version(version) < _Version(pver):
                    return False
            if lang_max_version is _FromPackageVersion:
                if _Version(version) > _Version(pver):
                    return False
        return True

    # TODO: Cache the results
    def find_interpreter(self, language, version):
        """
        :param language: the URI of the language
        :param version: string or None
        """
        main_nodes = list(self.graph.subjects(PREFIX + "lang", language))
        main_nodes = sorted(main_nodes, lambda u: self.order[u])
        for main_node in main_nodes:
            if self.check_version(version, main_node):
                return main_node

