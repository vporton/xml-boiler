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
import sys

from xmlboiler.core.alg import auto_transform, script_subcommand, transform_subcommand
from xmlboiler.core.alg.common import AssetsExhausted
from xmlboiler.core.options import NotInTargetNamespace, ChainOptions, ScriptOptions, TransformOptions
from xmlboiler.core.util.xml import MyXMLError


def run_filter_subcommand(state, _interpreters, pipe_options_list, pipe_processor):
    options = state.opts
    try:
        # TODO: Fine tune error messages
        if isinstance(options, ChainOptions):
            try:
                algorithm = auto_transform.Algorithms.automatic_transformation(state, _interpreters)
            except MyXMLError as e:
                sys.stderr.write("Error in the input XML document: " + str(e) + "\n")
                return False
            try:
                algorithm.run()
            except MyXMLError as e:
                sys.stderr.write("Error in an intermediary XML document during the transformation: " + str(e) + "\n")
                return False
        elif isinstance(options, ScriptOptions):
            try:
                algorithm = script_subcommand.Algorithms.script_filter(options.script_url, state, _interpreters)
                algorithm.run()
            except MyXMLError as e:
                sys.stderr.write("Error in the XML document: " + str(e) + "\n")
                return False
        elif isinstance(options, TransformOptions):
            try:
                algorithm = transform_subcommand.Algorithms.transform_filter(options.transform_url, state, _interpreters)
                algorithm.run()
            except MyXMLError as e:
                sys.stderr.write("Error in the XML document: " + str(e) + "\n")
                return False
    except AssetsExhausted:
        if not isinstance(options, ChainOptions):
            sys.stderr.write("The transformation failed, no more assets to load.\n")
            return False
        if options.not_in_target != NotInTargetNamespace.IGNORE:
            sys.stderr.write("The transformation failed, no more assets to load.\n")
            if options.not_in_target == NotInTargetNamespace.ERROR:
                return False
    return True
