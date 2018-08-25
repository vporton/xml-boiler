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

import itertools
import queue
from dataclasses import dataclass, field
from typing import Any

from dependency_injector import containers, providers
from rdflib import URIRef

from xmlboiler.core import execution_context_builders
from xmlboiler.core.options import RecursiveRetrievalPriorityOrderElement


# https://softwareengineering.stackexchange.com/questions/358931/breadth-first-traversal-with-some-edges-preferred/358937#358937
from xmlboiler.core.rdf_base.subclass import SubclassContainers

import xmlboiler.core.rdf_format.asset_parser.asset
from xmlboiler.core.rdf_recursive_descent.base import default_parse_context


# TODO: We yield an array of assets. Instead we could yield an array of Nones (what probably could be faster)

def _enumerate_xml_namespaces(state):
    stack = [state.dom.documentElement]
    while stack:
        v = stack.pop()
        for w in v.childNodes:
            if w.namespaceURI is not None:
                yield URIRef(w.namespaceURI)
            if w.attributes:
                for a in w.attributes.values():
                    if a.namespaceURI is not None and a.namespaceURI != 'http://www.w3.org/2000/xmlns/':
                        yield URIRef(a.namespaceURI)
            stack.append(w)

@dataclass(order=True)
class PrioritizedNS:
    root: bool=field(default=False, init=False)  # (fake) root node, enqueued first, so should be dequeued first (have greatest priority)
    priority: int = None
    ns: Any=field(default=None, compare=False)


# Return a pair (priority, namespace)
def _enumerate_child_namespaces(state, asset):
    priority = 0
    yield from [PrioritizedNS(priority, ns) for ns in _enumerate_xml_namespaces(state)]
    for order_part in state.opts.recursive_options.retrieval_priority:
        priority += 1   # note: below is used priority=0 to be above all these
        if order_part == RecursiveRetrievalPriorityOrderElement.SOURCES:
            for t in asset.transformers:
                for s in t.source_namespaces:
                    yield PrioritizedNS(priority, s)
        elif order_part == RecursiveRetrievalPriorityOrderElement.TARGETS:
            for t in asset.transformers:
                for s in t.target_namespaces:
                    yield PrioritizedNS(priority, s)
        elif order_part == RecursiveRetrievalPriorityOrderElement.WORKFLOW_TARGETS:
            # TODO: It may happen atmost once, may optimize not to run it again
            yield from [PrioritizedNS(priority, ns) for ns in state.opts.target_namespaces]
    priority += 1
    yield from [PrioritizedNS(priority, ns) for ns in asset.see_also_transform] # TODO: Support for validation


def _enumerate_child_namespaces_without_priority(state, asset):
    return [x.ns for x in _enumerate_child_namespaces(state, asset)]


class BaseDownloadAlgorithm(object):
    def __init__(self, state, parse_context, subclasses):
        self.state = state
        self.parse_context = parse_context
        self.subclasses = subclasses

    def add_ns(self, ns):
        if isinstance(ns, str):  # TODO: This is a hack
            ns = URIRef(ns)
        if ns not in self.state.assets:
            msg = self.parse_context.execution_context.translations.gettext("Loaded asset for namespace {ns}.").format(ns=ns)
            self.parse_context.execution_context.logger.info(msg)
            self.state.assets.add(ns)

    def process_assets(self, downloaders, ns):
        if ns is None:
            return []
        self.add_ns(ns)
        parser = xmlboiler.core.rdf_format.asset_parser.asset.AssetParser(self.parse_context, self.subclasses)
        assets = []
        for graph in [downloader(ns) for downloader in downloaders]:
            if graph is None:
                continue
            asset_info = parser.parse(graph)
            self.state.add_asset(asset_info)
            assets.append(asset_info)
            yield asset_info


class NoDownloader(BaseDownloadAlgorithm):
    def download_iterator(self):
        return itertools.chain.from_iterable(self._iter())

    def _iter(self):
        for downloaders in self.state.opts.recursive_options.downloaders:
            for ns in self.state.opts.recursive_options.initial_assets:
                yield self.process_assets(downloaders, ns)


class DepthFirstDownloader(BaseDownloadAlgorithm):
    # Recursive algorithm for simplicity.
    # Every yield produces a list of assets (not individual assets),
    # because in our_depth_first_based_download() we need to discard multiple assets.
    def depth_first_download(self, ns, downloaders):
        if ns in self.state.assets:
            return
        assets = self.process_assets(downloaders, ns)
        yield assets
        for asset in assets:
            for ns2 in _enumerate_child_namespaces_without_priority(self.state, asset):
                if ns2 not in self.state.assets:
                    yield from self.depth_first_download(ns2, downloaders)  # recursion

    # Every yield produces a list of assets (not individual assets),
    # because in our_depth_first_based_download() we need to discard multiple assets.
    def _our_depth_first_based_download(self):
        # initial assets and their children
        for downloaders in self.state.opts.recursive_options.downloaders:
            for ns in self.state.opts.recursive_options.initial_assets:
                yield self.process_assets(downloaders, ns)
            for asset in self.state.opts.recursive_options.initial_assets:
                try:
                    iter = self.depth_first_download(asset, downloaders)
                    next(iter)  # do not repeat the above
                    yield from iter
                except StopIteration:
                    pass

        # all other assets
        for ns in itertools.chain(_enumerate_xml_namespaces(self.state), self.state.opts.target_namespaces):
            yield from self.depth_first_download(ns, downloaders)  # recursion

    # Merge list of lists (in fact, iterators) into one list
    def download_iterator(self):
        return itertools.chain.from_iterable(self._our_depth_first_based_download())


class BreadthFirstDownloader(BaseDownloadAlgorithm):
    # https://www.hackerearth.com/practice/algorithms/graphs/breadth-first-search/tutorial/
    def _breadth_first_download(self, downloaders):
        parser = xmlboiler.core.rdf_format.asset_parser.asset.AssetParser(self.parse_context, self.subclasses)
        Q = queue.PriorityQueue()
        # we start with this item as the top node of the search (later remove it)
        fake_root = PrioritizedNS()
        fake_root.root = True
        Q.put(fake_root)  # root node
        # yield deliberately not called
        # no need to mark fake_root as visited, because it is not actually traversed
        while not Q.empty():  # in Python 3.7 bool(Q) does not work
            v = Q.get()
            if v.root:  # enumerate the top level differently
                # use priority above all other priorities
                childs = [(100, info) for info in self.state.opts.recursive_options.initial_assets]
                childs.extend([PrioritizedNS(0, ns) for ns in _enumerate_xml_namespaces(self.state)])  # below all priorities in _enumerate_child_namespaces()
            else:
                childs = _enumerate_child_namespaces(self.state, v.ns)
            for child in childs:
                ns2 = child.ns
                if ns2 not in self.state.assets:
                    assets = self.process_assets(downloaders, ns2)
                    for asset_info in assets:
                        Q.put(PrioritizedNS(child.priority, asset_info))
                    yield assets

    def download_iterator(self):
        iter = [self._breadth_first_download(downloaders) for downloaders in self.state.opts.recursive_options.downloaders]
        return itertools.chain.from_iterable(iter)


class download_providers(containers.DeclarativeContainer):
    no_download = providers.Callable(NoDownloader,
                                     parse_context=default_parse_context,
                                     subclasses=SubclassContainers.basic_subclasses)
    depth_first_download = providers.Callable(DepthFirstDownloader,
                                              parse_context=default_parse_context,
                                              subclasses=SubclassContainers.basic_subclasses)
    breadth_first_download = providers.Callable(BreadthFirstDownloader,
                                                parse_context=default_parse_context,
                                                subclasses=SubclassContainers.basic_subclasses)
