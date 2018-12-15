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
from copy import deepcopy

from xmlboiler.command_line.modifiers import modify_pipeline_element, ChainOptionsProcessor


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
    def __init__(self, element_options, execution_context, error_logger, chain_parser):
        self.element_options = element_options
        self.execution_context = execution_context
        self.error_logger = error_logger
        self.chain_parser = chain_parser

    def execute(self, pipe_str):
        options_list = self.parse(pipe_str)
        # TODO

    def parse(self, pipe_str):
        args_list = split_pipeline(pipe_str)
        options_list = []
        for args in args_list:
            if len(args) == 0:
                self.error_logger.error(self.execution_context.translate("Wrong command '' in the pipeline."))
                return False
            local_element_options = deepcopy(self.element_options)
            modify_pipeline_element(args, local_element_options)
            method = {'chain': PipelineProcessor.chain_opts,
                      'c': PipelineProcessor.chain_opts}\
                [args[0]]
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
        processor = ChainOptionsProcessor(element_options, self.execution_context, self.error_logger)
        return processor.process(pargs)
