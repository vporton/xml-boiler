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

from ordered_set import OrderedSet
from rdflib import URIRef

import xmlboiler.core.urls
import xmlboiler.core.os_command.regular
from xmlboiler.core.alg import auto_transform
from xmlboiler.core.alg.auto_transform import AssetsExhausted
from xmlboiler.core.alg.download import download_providers
from xmlboiler.core.alg.state import PipelineState
from xmlboiler.core.asset_downloaders import local_asset_downloader, directory_asset_downloader
import xmlboiler.core.interpreters.parse
from xmlboiler.core.execution_context_builders import context_for_logger, Contexts
from xmlboiler.core.options import TransformationAutomaticWorkflowElementOptions, \
    RecursiveRetrievalPriorityOrderElement, NotInTargetNamespace
import xmlboiler.core.alg.next_script1
import xmlboiler.core.alg.next_script2
from xmlboiler.core.packages.config import determine_os
from xmlboiler.core.rdf_recursive_descent.base import default_parse_context
from xmlboiler.core.util.xml import MyXMLError


def main(argv):
    locale.setlocale(locale.LC_ALL, '')

    # https://docs.python.org/3/library/asyncio-platforms.html#asyncio-windows-subprocess
    if os.name == 'nt':
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""Automatically process XML.\n
    To support this project:
    - Send money to PayPal porton@narod.ru or https://paypal.me/victorporton
    - Send Ether to 0x36A0356d43EE4168ED24EFA1CAe3198708667ac0
    - Buy tokens at https://crypto4ngo.org/project/view/4
    
    Use http_proxy or ftp_proxy variables to specify proxy servers.""")
    subparsers = parser.add_subparsers(title='subcommands')
    subparsers.required = True

    parser.add_argument('-l', '--log-level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        type=str.upper)
    parser.add_argument('-p', '--preload', help='preload asset', action='append', metavar='NAMESPACE')
    parser.add_argument('-r', '--recursive', help='recursive download mode (none, breadth-first, depth-first)',
                        choices=['none', 'breadth', 'depth'])
    parser.add_argument('-x', '--recursive-order', metavar='ORDER',
                        help='recursive download order (comma separated "sources", "targets", "workflowtargets")')
    parser.add_argument('-y', '--directory', help='additional directory with assets', metavar='NAME=DIR', action='append')
    parser.add_argument('-d', '--downloaders', metavar='DOWNLOADERS',
                        help='a plus-separated list of comma-separated lists of "builtin","DIR"')
    parser.add_argument('--software',
                        help='determine installed software by package manager and/or executables in PATH. ' + \
                             '\'package\' are now supported only on Debian-based systems. ' + \
                             'Defaults to \'both\' on Debian-based and \'executable\' on others.',
                        choices=['package', 'executable', 'both'])
    parser.add_argument('-T', '--timeout', help='HTTP and FTP timeout in seconds (default 10.0)', type=float, default=10)

    chain_parser = subparsers.add_parser('chain', aliases=['c'], help='Automatically run a chain of transformations')
    chain_parser.set_defaults(options_object=TransformationAutomaticWorkflowElementOptions)
    chain_parser.add_argument('source', nargs='?', help='source document (defaults to stdin)')
    chain_parser.add_argument('-o', '--output', nargs=1, help='output file (defaults to stdout)')
    chain_parser.add_argument('-t', '--target', help='target namespace(s)', action='append', metavar='NAMESPACE')
    chain_parser.add_argument('-s', '--next-script', help='"next script" algorithm ("precedence" is not supported)',
                              choices=['precedence', 'doc'], default='doc')
    chain_parser.add_argument('-n', '--not-in-target', help='what if a result is not in target NS',
                              choices=['ignore', 'remove', 'error'])
    chain_parser.add_argument('-u', '--universal-precedence', help='universal precedence', metavar='URL')
    chain_parser.add_argument('-W', '--weight-formula', help='formula for weighting scripts',
                              choices=['inverseofsum', 'sumofinverses'], default='inverseofsum')

    try:
        args = parser.parse_args(argv)
    except TypeError:
        parser.print_usage()
        return 1

    execution_context = context_for_logger(Contexts.execution_context(),
                                           Contexts.logger('main', args.log_level))
    error_handler = logging.StreamHandler()
    error_handler.setFormatter(logging.Formatter('%(message)s'))
    error_logger = Contexts.logger('error', logging.WARNING)
    error_logger.addHandler(error_handler)

    options = args.options_object(execution_context=execution_context,
                                  log_level=args.log_level,
                                  error_logger=error_logger,
                                  command_runner=xmlboiler.core.os_command.regular.regular_provider(context=execution_context),
                                  url_opener=xmlboiler.core.urls.OurOpeners.our_opener(timeout=args.timeout))

    directories_map = {}
    if args.directory is not None:
        for eq in args.directory:
            m = re.match(r'([^=]+)=(.*)', eq, re.S)
            if not m:
                sys.stderr.write("Wrong --directory flag format\n")
                return 1
            directories_map[m[1]] = m[2]

    options.recursive_options.initial_assets = OrderedSet([] if args.preload is None else map(URIRef, args.preload))

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
        options.recursive_options.retrieval_priority = OrderedSet([m[s] for s in elts])
    else:
        # TODO: Subject to change
        options.recursive_options.retrieval_priority = \
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
            options.recursive_options.downloaders = \
                [[infer_downloader(s) for s in d] for d in downloaders]
        except ValueError:
            return 1
    else:
        options.recursive_options.downloaders = [[local_asset_downloader]]

    output = None if not args.output or args.output[0] == '-' else args.output[0]

    options.target_namespaces = frozenset([] if args.target is None else [URIRef(t) for t in args.target])

    options.not_in_target = {'ignore': NotInTargetNamespace.IGNORE,
                             'remove': NotInTargetNamespace.REMOVE,
                             'error': NotInTargetNamespace.ERROR}[args.not_in_target or 'error']

    options.universal_precedence = args.universal_precedence
    options.weight_formula = args.weight_formula

    options.installed_soft_options.package_manager = determine_os() if args.software != 'executable' else None
    options.installed_soft_options.use_path = args.software in ('executable', 'both')
    if options.installed_soft_options.package_manager is None and args.software in ('package', 'both'):
        sys.stderr.write("Package manager is not supported on this OS.\n")

    state = PipelineState(opts=options)  # TODO: Support for other commands than 'chain'

    if args.source and re.match(r'^[a-zA-Z]+:', args.source):
        state.xml_text = options.url_opener.open(args.source).read()
    else:
        source = sys.stdin if args.source is None or args.source == '-' else open(args.source)
        state.xml_text = source.buffer.read()
        source.close()

    m = {
        'precedence': xmlboiler.core.alg.next_script1.ScriptsIterator,
        'doc': xmlboiler.core.alg.next_script2.ScriptsIterator,
    }
    options.next_script = m[args.next_script](state)

    download_execution_context = context_for_logger(execution_context,
                                                    Contexts.logger('asset', args.log_level))
    downloader_parse_context = default_parse_context(execution_context=download_execution_context)
    options.recursive_options.download_algorithm = \
        {'none': download_providers.no_download,
         'breadth': download_providers.breadth_first_download,
         'depth': download_providers.depth_first_download}[args.recursive or 'breadth'](\
            state, parse_context=downloader_parse_context).download_iterator()

    _interpreters = xmlboiler.core.interpreters.parse.Providers.interpreters_factory(options.installed_soft_options,
                                                                                     log_level=args.log_level)
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

    if output is None:
        sys.stdout.buffer.write(state.xml_text)
    else:
        with open(output, 'wb') as file:
            file.write(state.xml_text)

    return 0