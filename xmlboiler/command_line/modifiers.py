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

from xmlboiler.core.options import NotInTargetNamespace, BaseAlgorithmOptions, ChainOptions, ScriptOptions, \
    TransformOptions


class ChainOptionsProcessor(object):
    def __init__(self, element_options):
        self.element_options = element_options

    def process(self, args):
        return ChainOptions(element_options=self.element_options,
                            universal_precedence=args.universal_precedence,
                            target_namespaces=frozenset([] if args.target is None else [URIRef(t) for t in args.target]))


class ScriptOptionsProcessor(object):
    def __init__(self, element_options):
        self.element_options = element_options

    def process(self, args):
        return ScriptOptions(element_options=self.element_options,
                             script_url=args.script)


class TransformOptionsProcessor(object):
    def __init__(self, element_options):
        self.element_options = element_options

    def process(self, args):
        return TransformOptions(element_options=self.element_options,
                                transform_url=args.transform)


def modify_pipeline_element(args, obj):
    """Process command line options for a pipeline element or for a filter"""
    if args.subcommand == 'chain':
        obj.not_in_target = {'ignore': NotInTargetNamespace.IGNORE,
                             'remove': NotInTargetNamespace.REMOVE,
                             'error': NotInTargetNamespace.ERROR}[args.not_in_target or 'error']
    elif args.subcommand == 'script':
        obj.script_url = args.script
    elif args.subcommand == 'transform':
        obj.transform_url = args.transform
