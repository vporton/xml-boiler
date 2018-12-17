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
from xmlboiler.core.options import NotInTargetNamespace
from xmlboiler.core.util.xml import MyXMLError


def run_subcommand(args, state, _interpreters, pipe_options_list, pipe_processor):
    options = state.opts
    if args.subcommand == 'chain':
        # TODO: Duplicate code with command_line/pipe.py
        try:
            try:
                algorithm = auto_transform.Algorithms.automatic_transformation(state, _interpreters)
            except MyXMLError as e:
                sys.stderr.write("Error in the input XML document: " + str(e) + "\n")
                return 1
            try:
                algorithm.run()
            except MyXMLError as e:
                sys.stderr.write("Error in an intermediary XML document during the transformation: " + str(e) + "\n")
                return 1
        except AssetsExhausted:
            if options.not_in_target != NotInTargetNamespace.IGNORE:
                sys.stderr.write("The transformation failed, no more assets to load.\n")
                if options.not_in_target == NotInTargetNamespace.ERROR:
                    return 1
    elif args.subcommand == 'script':
        try:
            algorithm = script_subcommand.Algorithms.script_filter(args.script, state, _interpreters)
        except MyXMLError as e:
            sys.stderr.write("Error in the input XML document: " + str(e) + "\n")
            return 1
        algorithm.run()
    elif args.subcommand == 'transform':
        try:
            algorithm = transform_subcommand.Algorithms.transform_filter(args.transform, state, _interpreters)
        except MyXMLError as e:
            sys.stderr.write("Error in the input XML document: " + str(e) + "\n")
            return 1
        algorithm.run()
    elif args.subcommand == 'pipe':
        res = pipe_processor.execute(pipe_options_list, state, _interpreters)
        if res:
            return res
    return 0
