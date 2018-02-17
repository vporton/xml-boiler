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
from xmlboiler.core.rdf_recursive_descent.base import ErrorHandler
from xmlboiler.core.rdf_recursive_descent.compound import ZeroOnePredicate
from xmlboiler.core.rdf_recursive_descent.list import ListParser
from xmlboiler.core.rdf_recursive_descent.literal import StringLiteral

PREFIX = "http://portonvictor.org/ns/trans/internal/"


class Interpeters(object):
    def __init__(self, graph, parse_context):
        self.graph = graph
        self.parse_context = parse_context

        list_node = graph[:URIRef("http://portonvictor.org/ns/trans/internal/interpretersList")][0]
        the_list = ListParser(ErrorHandler.FATAL).parse(parse_context, graph, list_node)
        self.order = {k: v for v, k in enumerate(the_list)}

    # TODO: Cache the results
    def find_interpreter(self, language, version):
        """
        :param language: the URI of the language
        :param version: string
        """
        main_nodes = list(self.graph.subjects(PREFIX + "lang", language))
        main_nodes = sorted(main_nodes, lambda u: self.order[u])
        for main_node in main_nodes:
            # FIXME: :fromPackageVersion
            lang_min_version = ZeroOnePredicate(PREFIX + "langMinVersion", StringLiteral, ErrorHandler.FATAL)
            lang_max_version = ZeroOnePredicate(PREFIX + "langMaxVersion", StringLiteral, ErrorHandler.FATAL)
            if version is None or (\
                            ThePackageManaging.VersionClass(version) \
                            >= ThePackageManaging.VersionClass(lang_min_version) \
                            <= ThePackageManaging.VersionClass(lang_max_version)):
                return main_node

