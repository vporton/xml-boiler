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

import xmlboiler
from xmlboiler.core.options import NotInTargetNamespace, BaseAlgorithmOptions, ChainOptions


class ChainOptionsProcessor(object):
    def __init__(self, element_options, execution_context, error_logger):
        self.element_options = element_options
        self.execution_context = execution_context
        self.error_logger = error_logger

    def process(self, args):
        return ChainOptions(element_options=self.element_options,
                            universal_precedence=args.universal_precedence,
                            target_namespaces=frozenset([] if args.target is None else [URIRef(t) for t in args.target]))


def modify_pipeline_element(args, obj):
    """Process command line options for a pipeline element or for a filter"""
    obj.not_in_target = {'ignore': NotInTargetNamespace.IGNORE,
                         'remove': NotInTargetNamespace.REMOVE,
                         'error': NotInTargetNamespace.ERROR}[args.not_in_target or 'error']
