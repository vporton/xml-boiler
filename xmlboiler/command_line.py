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
import re
import sys

from ordered_set import OrderedSet
from rdflib import URIRef

import xmlboiler.core.urls
from xmlboiler.core.alg.auto_transform import AutomaticTranformation, AssetsExhausted
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


def main(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""Automatically process XML.\n
    To support this project:
    - Send money to PayPal porton@narod.ru or https://paypal.me/victorporton
    - Send Ether to 0x36A0356d43EE4168ED24EFA1CAe3198708667ac0
    - Buy tokens at https://crypto4ngo.org/project/view/4""")
    subparsers = parser.add_subparsers(title='subcommands')

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

    chain_parser = subparsers.add_parser('chain', aliases=['c'], help='Automatically run a chain of transformations')
    chain_parser.set_defaults(options_object=TransformationAutomaticWorkflowElementOptions)
    chain_parser.add_argument('source', nargs='?', help='source document (defaults to stdin)')
    chain_parser.add_argument('-o', '--output', nargs=1, help='output file (defaults to stdout)')
    chain_parser.add_argument('-t', '--target', help='target namespace(s)', action='append', metavar='NAMESPACE')
    chain_parser.add_argument('-s', '--next-script', help='"next script" algorithm ("precedence" is not supported)',
                              choices=['precedence', 'doc'], default='doc')  # TODO: subject to change notation
    chain_parser.add_argument('-n', '--not-in-target', help='what if a result is not in target NS',
                              choices=['ignore', 'remove', 'error'])
    chain_parser.add_argument('-u', '--universal-precedence', help='universal precedence', metavar='URL')

    try:
        args = parser.parse_args(argv)
    except TypeError:
        parser.print_usage()
        return 1

    execution_context = context_for_logger(Contexts.execution_context(), Contexts.default_logger('main'))

    options = args.options_object(execution_context=execution_context)

    directories_map = {}
    if args.directory is not None:
        for eq in args.directory:
            m = re.match(r'([^=]+)=(.*)', eq, re.S)
            if not m:
                sys.stderr.write("Wrong --directory flag format\n")
                return 1
            directories_map[m[1]] = m[2]

    options.recursive_options.initial_assets = OrderedSet([] if args.preload is None else args.preload)

    if args.recursive_order is not None:
        elts = args.recursive_order.split(',')
        elts2 = frozenset(elts)
        if not elts2.issubset(["sources", "targets", "workflowtargets"]):
            print("Error: --recursive-order can be only: sources, targets, workflowtargets.")
            return 1
        if len(elts2) != len(elts):
            print("Error: values are repeated more than once in --recursive-order option.")
            return 1
        map = {"sources": RecursiveRetrievalPriorityOrderElement.SOURCES,
               "targets": RecursiveRetrievalPriorityOrderElement.TARGETS,
               "workflowtargets": RecursiveRetrievalPriorityOrderElement.WORKFLOW_TARGETS}
        options.recursive_options.retrieval_priority = OrderedSet([map[s] for s in elts])
    else:
        # TODO: Subject to change
        options.recursive_options.retrieval_priority = \
            OrderedSet([RecursiveRetrievalPriorityOrderElement.WORKFLOW_TARGETS,
                        RecursiveRetrievalPriorityOrderElement.TARGETS,
                        RecursiveRetrievalPriorityOrderElement.SOURCES])

    def infer_downloader(s):
        return directory_asset_downloader(directories_map[s]) if s != 'builtin' else local_asset_downloader

    # Don't execute commands from remote scripts (without not yet properly working jail).
    # So downloading from URLs does not make sense yet.
    # TODO: Better error reporting
    if args.downloaders:
        downloaders = [d.split(',') for d in args.downloaders.split('+')]
        options.recursive_options.downloaders = \
            [[infer_downloader(s) for s in d] for d in downloaders]
    else:
        options.recursive_options.downloaders = [[local_asset_downloader]]

    source = sys.stdin if args.source is None or args.source == '-' else \
        (xmlboiler.core.urls.our_opener.open(args.source) if re.match(r'^[a-zA-Z]+:', args.source) else open(args.source))
    output = None if not args.output or args.output[0] == '-' else args.output[0]

    options.target_namespaces = frozenset([] if args.target is None else [URIRef(t) for t in args.target])

    options.not_in_target = {'ignore': NotInTargetNamespace.IGNORE,
                             'remove': NotInTargetNamespace.REMOVE,
                             'error': NotInTargetNamespace.ERROR}[args.not_in_target or 'error']

    options.universal_precedence = args.universal_precedence

    options.installed_soft_options.package_manager = determine_os() if args.software != 'executable' else None
    options.installed_soft_options.path = args.software in ('executable', 'both')
    if options.installed_soft_options.package_manager is None and args.software in ('package', 'both'):
        sys.stderr.write("Package manager is not supported on this OS.\n")

    state = PipelineState(opts=options)  # TODO: Support for other commands than 'chain'
    state.xml_text = source.buffer.read(); source.close()

    map = {
        'precedence': xmlboiler.core.alg.next_script1.ScriptsIterator,
        'doc': xmlboiler.core.alg.next_script2.ScriptsIterator,
    }
    options.next_script = map[args.next_script](state)

    # TODO: Refactor
    download_execution_context = context_for_logger(execution_context, Contexts.default_logger('asset'))
    options.recursive_options.download_algorithm = \
        {'none': download_providers.no_download,
         'breadth': download_providers.breadth_first_download,
         'depth': download_providers.depth_first_download}[args.recursive or 'breadth'](\
            state, parse_context=default_parse_context(execution_context=download_execution_context)).download_iterator()

    # TODO: Use a factory of algorithms
    _interpreters = xmlboiler.core.interpreters.parse.Providers.interpreters_factory(options.installed_soft_options)
    algorithm = AutomaticTranformation(state, _interpreters)
    try:
        algorithm.run()
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