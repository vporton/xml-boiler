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

import argparse
import locale
import logging
import os
import re
import sys
from urllib.error import URLError

from ordered_set import OrderedSet
from rdflib import URIRef

import xmlboiler.core.urls
import xmlboiler.core.os_command.regular
from xmlboiler.command_line.common import run_filter_subcommand
from xmlboiler.command_line.modifiers import modify_pipeline_element, ChainOptionsProcessor, ScriptOptionsProcessor, \
    TransformOptionsProcessor
from xmlboiler.command_line.pipe import PipelineProcessor
from xmlboiler.core.alg import auto_transform
from xmlboiler.core.alg.download import download_providers
from xmlboiler.core.alg.state import PipelineState
from xmlboiler.core.asset_downloaders import local_asset_downloader, directory_asset_downloader
import xmlboiler.core.interpreters.parse
from xmlboiler.core.execution_context_builders import context_for_logger, Contexts
from xmlboiler.core.options import \
    RecursiveRetrievalPriorityOrderElement, BaseAutomaticWorkflowElementOptions, \
    BaseAlgorithmOptions, PipelineOptions
import xmlboiler.core.alg.next_script1
import xmlboiler.core.alg.next_script2
from xmlboiler.core.packages.config import determine_os
from xmlboiler.core.rdf_base.subclass import SubclassContainers
from xmlboiler.core.rdf_recursive_descent.base import default_parse_context


def main(argv):
    locale.setlocale(locale.LC_ALL, '')

    # https://docs.python.org/3/library/asyncio-platforms.html#asyncio-windows-subprocess
    if os.name == 'nt':
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    base_chain_parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                                description="Common chain argument")
    base_chain_parser.add_argument('-n', '--not-in-target', help='what if a result is not in target NS',
                                   choices=['ignore', 'remove', 'error'], default='error')

    parser = argparse.ArgumentParser(parents=[base_chain_parser],
                                     add_help=False,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""Automatically process XML.\n
    To support this project:
    - Donate at https://crypto4ngo.org/project/view/4
    - Send money to PayPal porton@narod.ru or https://paypal.me/victorporton
    - Crypto at https://gitcoin.co/grants/178/automatic-transformation-of-xml-namespaces-and-xm
    - Send BitCoin to 1BdUaP3uRuUC1TXcLgxKXdWWfQKXL2tmqa
    
    Use http_proxy or ftp_proxy variables to specify proxy servers.""")
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')
    subparsers.required = True

    parser.add_argument('-i', '--input', nargs=1, help='source document (defaults to stdin)')
    parser.add_argument('-o', '--output', nargs=1, help='output file (defaults to stdout)')
    parser.add_argument('-l', '--log-level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        type=str.upper)
    parser.add_argument('-p', '--preload', help='preload asset', action='append', metavar='NAMESPACE')
    parser.add_argument('-r', '--recursive', help='recursive download mode (none, breadth-first, depth-first)',
                        choices=['none', 'breadth', 'depth'])
    parser.add_argument('-x', '--recursive-order', metavar='ORDER',
                        help='recursive download order (comma separated "sources", "targets", "workflowtargets")')
    parser.add_argument('-y', '--directory', help='additional directory with assets', metavar='NAME=DIR',
                        action='append')
    parser.add_argument('-d', '--downloaders', metavar='DOWNLOADERS',
                        help='a plus-separated list of comma-separated lists of "builtin","DIR"')
    parser.add_argument('--software',
                        help='determine installed software by package manager and/or executables in PATH. ' + \
                             '\'package\' are now supported only on Debian-based systems. ' + \
                             'Defaults to \'both\' on Debian-based and \'executable\' on others.',
                        choices=['package', 'executable', 'both'])
    parser.add_argument('-s', '--next-script',
                        help='"next script" algorithm ("precedence" is not supported)',
                        choices=['precedence', 'doc'], default='doc')
    parser.add_argument('-W', '--weight-formula', help='formula for weighting scripts',
                        choices=['inverseofsum', 'sumofinverses'], default='inverseofsum')
    parser.add_argument('-T', '--timeout', help='HTTP and FTP timeout in seconds (default 10.0)', type=float,
                        default=10)

    chain_parser = subparsers.add_parser('chain', aliases=['c'],
                                         parents=[base_chain_parser],
                                         help='Automatically run a chain of transformations',
                                         add_help=False)
    chain_parser.set_defaults(subcommand='chain')
    chain_parser.add_argument('-t', '--target', help='target namespace(s)', action='append', metavar='NAMESPACE')
    chain_parser.add_argument('-u', '--universal-precedence', help='universal precedence', metavar='URL')

    script_parser = subparsers.add_parser('script', aliases=['s'],
                                          # parents=[base_script_parser],
                                          help='Run a script',
                                          add_help=True)
    script_parser.set_defaults(subcommand='script')
    script_parser.add_argument('script', help='script to run', metavar='SCRIPT')

    transform_parser = subparsers.add_parser('transform', aliases=['t'],
                                          # parents=[base_script_parser],
                                          help='Run a transformation',
                                          add_help=True)
    transform_parser.set_defaults(subcommand='transform')
    transform_parser.add_argument('transform', help='transformation to run', metavar='TRANSFORMATION')

    pipe_parser = subparsers.add_parser('pipe', aliases=['p'],
                                        parents=[base_chain_parser],
                                        help='Run a pipeline of XML filters',
                                        add_help=False)
    pipe_parser.set_defaults(subcommand='pipe')
    pipe_parser.add_argument('pipe', metavar='PIPE', help="+-separated pipeline of filters as a single argument")

    try:
        args = parser.parse_args(argv)
    except TypeError:
        parser.print_usage()
        return 1

    logging.basicConfig()
    log_handler = logging.StreamHandler()
    log_handler.setLevel(args.log_level)
    log_handler.setFormatter(logging.Formatter('%(name)s:%(levelname)s:%(message)s'))
    base_logger = Contexts.logger('main', args.log_level, log_handler=log_handler)
    translations = Contexts.default_translations(logger=base_logger)
    execution_context = Contexts.execution_context(logger=base_logger,
                                                   translations=translations,
                                                   log_handler=log_handler,
                                                   log_level=args.log_level)
    error_log_handler = logging.StreamHandler()
    error_log_handler.setLevel(args.log_level)
    error_log_handler.setFormatter(logging.Formatter('%(message)s'))
    error_logger = Contexts.logger('error', logging.WARNING, log_handler=error_log_handler)

    algorithm_options = BaseAlgorithmOptions(
        execution_context=execution_context,
        error_logger=error_logger,
        command_runner=xmlboiler.core.os_command.regular.regular_provider(context=execution_context),
        url_opener=xmlboiler.core.urls.OurOpeners.our_opener(timeout=args.timeout))

    element_options = BaseAutomaticWorkflowElementOptions(algorithm_options=algorithm_options)
    element_options.algorithm_options.recursive_options.initial_assets = OrderedSet(
        [] if args.preload is None else map(URIRef, args.preload))
    element_options.algorithm_options.weight_formula = args.weight_formula

    if args.recursive_order is not None:
        elts = args.recursive_order.split(',')
        elts2 = frozenset(elts)
        if not elts2.issubset(["sources", "targets", "workflowtargets"]):
            print("Error: --recursive-order can be only: sources, targets, workflowtargets.")
            return 1
        if len(elts2) != len(elts):
            print("Error: values are repeated more than once in --recursive-order option.")
            return 1
        m = {"sources": RecursiveRetrievalPriorityOrderElement.SOURCES,
             "targets": RecursiveRetrievalPriorityOrderElement.TARGETS,
             "workflowtargets": RecursiveRetrievalPriorityOrderElement.WORKFLOW_TARGETS}
        element_options.recursive_options.retrieval_priority = OrderedSet([m[s] for s in elts])
    else:
        # TODO: Subject to change
        element_options.recursive_options.retrieval_priority = \
            OrderedSet([RecursiveRetrievalPriorityOrderElement.WORKFLOW_TARGETS,
                        RecursiveRetrievalPriorityOrderElement.TARGETS,
                        RecursiveRetrievalPriorityOrderElement.SOURCES])

    def infer_downloader(s):
        if s not in directories_map:
            sys.stderr.write("No such downloader '{d}' (use --directory option)\n".format(d=s))
            raise ValueError()
        return directory_asset_downloader(directories_map[s]) if s != 'builtin' else local_asset_downloader

    # Don't execute commands from remote scripts (without not yet properly working jail).
    # So downloading from URLs does not make sense yet.
    if args.downloaders:
        downloaders = [d.split(',') for d in args.downloaders.split('+')]
        try:
            element_options.recursive_options.downloaders = \
                [[infer_downloader(s) for s in d] for d in downloaders]
        except ValueError:
            return 1
    else:
        element_options.recursive_options.downloaders = [[local_asset_downloader]]

    element_options.algorithm_options.installed_soft_options.package_manager = \
        determine_os() if args.software != 'executable' else None
    element_options.algorithm_options.installed_soft_options.use_path = args.software in ('executable', 'both')
    if element_options.installed_soft_options.package_manager is None and args.software in ('package', 'both'):
        sys.stderr.write("Package manager is not supported on this OS.\n")

    directories_map = {}
    if args.directory is not None:
        for eq in args.directory:
            m = re.match(r'([^=]+)=(.*)', eq, re.S)
            if not m:
                sys.stderr.write("Wrong --directory flag format\n")
                return 1
            directories_map[m[1]] = m[2]

    output = None if not args.output or args.output[0] == '-' else args.output[0]

    pipe_options_list = None
    pipe_processor = None
    if args.subcommand == 'chain':
        options_processor = ChainOptionsProcessor(element_options)
        options = options_processor.process(args)
    elif args.subcommand == 'script':
        options_processor = ScriptOptionsProcessor(element_options)
        options = options_processor.process(args)
    elif args.subcommand == 'transform':
        options_processor = TransformOptionsProcessor(element_options)
        options = options_processor.process(args)
    elif args.subcommand == 'pipe':
        options = PipelineOptions(element_options=element_options)
        pipe_processor = PipelineProcessor(element_options, execution_context, error_logger, chain_parser,
                                           script_parser, transform_parser)
        pipe_options_list = pipe_processor.parse(args.pipe)
        if not pipe_options_list:
            return 1
    else:
        sys.stderr.write("Command not supported!\n")
        return 1

    modify_pipeline_element(args, element_options)

    state = PipelineState(opts=options)

    m = {
        'precedence': xmlboiler.core.alg.next_script1.ScriptsIterator,
        'doc': xmlboiler.core.alg.next_script2.ScriptsIterator,
    }
    state.next_script = m[args.next_script](state)

    input = None if not args.input or args.input[0] == '-' else args.input[0]
    if input and re.match(r'^[a-zA-Z]+:', input):
        try:
            state.xml_text = options.url_opener.open(input).read()
        except URLError as e:
            sys.stderr.write(str(e) + "\n")
            return 1
    else:
        try:
            source = sys.stdin if input is None or input == '-' else open(input)
        except OSError as e:
            sys.stderr.write(str(e) + "\n")
            return 1
        state.xml_text = source.buffer.read()
        source.close()

    download_execution_context = context_for_logger(execution_context, 'asset')
    downloader_parse_context = default_parse_context(execution_context=download_execution_context)
    basic_subclasses = SubclassContainers.basic_subclasses(context=download_execution_context)
    state.download_algorithm = \
        {'none': download_providers.no_download,
         'breadth': download_providers.breadth_first_download,
         'depth': download_providers.depth_first_download}[args.recursive or 'breadth']( \
            state,
            parse_context=downloader_parse_context,
            subclasses=basic_subclasses).download_iterator()

    _interpreters = xmlboiler.core.interpreters.parse.Providers.interpreters_factory(
        options.element_options.installed_soft_options,
        execution_context=execution_context)
    if args.subcommand == 'pipe':
        res = pipe_processor.execute(pipe_options_list, state, _interpreters)
        if res:
            return res
    else:
        if not run_filter_subcommand(state, _interpreters, pipe_options_list, pipe_processor):
            return 1

    try:
        if output is None:
            sys.stdout.buffer.write(state.xml_text)
        else:
            with open(output, 'wb') as file:
                file.write(state.xml_text)
    except OSError as e:
        sys.stderr.write(str(e) + "\n")
        return 1

    return 0
