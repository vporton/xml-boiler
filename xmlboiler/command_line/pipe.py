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

import re
import sys
from copy import deepcopy

from xmlboiler.command_line.common import run_filter_subcommand
from xmlboiler.command_line.modifiers import modify_pipeline_element, ChainOptionsProcessor, ScriptOptionsProcessor, \
    TransformOptionsProcessor
from xmlboiler.core.alg import auto_transform, script_subcommand, transform_subcommand
from xmlboiler.core.alg.common import AssetsExhausted
from xmlboiler.core.options import NotInTargetNamespace, ChainOptions, ScriptOptions, TransformOptions
from xmlboiler.core.util.xml import MyXMLError


def split_pipeline(s):
    res = [['']]
    r = r'\\\\|\\\+|\\\s|\s+\+\s+|\s+|[^\s\\]+'
    for m in re.finditer(r, s, re.M|re.S):
        if m[0][0] == '\\':
            res[-1][-1] += m[0][1:]
        elif re.match(r'^\s+\+\s+$', m[0], re.M|re.S):
            res.append([''])
        elif re.match(r'^\s+$', m[0], re.M | re.S):
            res[-1].append('')
        else:
            res[-1][-1] += m[0]
    return res

# print(split_pipeline(r'a\\ \+  b + c\ d +'))


class PipelineProcessor(object):
    def __init__(self, element_options, execution_context, error_logger, chain_parser, script_parser, transform_parser):
        self.element_options = element_options
        self.execution_context = execution_context
        self.error_logger = error_logger
        self.chain_parser = chain_parser
        self.script_parser = script_parser
        self.transform_parser = transform_parser

    def execute(self, options_list, state, _interpreters):
        for options in options_list:
            state.opts = options
            if not run_filter_subcommand(state, _interpreters, options_list, None):
                return 1
        return 0

    def parse(self, pipe_str):
        args_list = split_pipeline(pipe_str)
        options_list = []
        for args in args_list:
            if len(args) == 0:
                self.error_logger.error(self.execution_context.translate("Wrong command '' in the pipeline."))
                return False
            local_element_options = self.element_options.my_deepcopy()
            try:
                method = {'chain': PipelineProcessor.chain_opts,
                          'c': PipelineProcessor.chain_opts,
                          'script': PipelineProcessor.script_opts,
                          's': PipelineProcessor.script_opts,
                          'transform': PipelineProcessor.transform_opts,
                          't': PipelineProcessor.transform_opts}\
                    [args[0]]
            except KeyError:
                msg = self.execution_context.translations.gettext("Wrong command '{cmd}' in the pipeline.".format(cmd=args[0]))
                self.error_logger.error(msg)
                return False
            options_object = method(self, args[1:], local_element_options)
            if not options_object:
                return False
            options_list.append(options_object)
        return options_list

    def chain_opts(self, args, element_options):
        try:
            pargs = self.chain_parser.parse_args(args)
        except TypeError:
            self.chain_parser.print_usage()
            return False
        modify_pipeline_element(pargs, element_options)
        processor = ChainOptionsProcessor(element_options)
        return processor.process(pargs)

    def script_opts(self, args, element_options):
        try:
            pargs = self.script_parser.parse_args(args)
        except TypeError:
            self.script_parser.print_usage()
            return False
        modify_pipeline_element(pargs, element_options)
        processor = ScriptOptionsProcessor(element_options)
        return processor.process(pargs)

    def transform_opts(self, args, element_options):
        try:
            pargs = self.transform_parser.parse_args(args)
        except TypeError:
            self.transform_parser.print_usage()
            return False
        modify_pipeline_element(pargs, element_options)
        processor = TransformOptionsProcessor(element_options)
        return processor.process(pargs)
