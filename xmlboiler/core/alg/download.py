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

from dataclasses import dataclass, field
from typing import Any

from xmlboiler.core.options import RecursiveRetrievalPriorityOrderElement


# https://softwareengineering.stackexchange.com/questions/358931/breadth-first-traversal-with-some-edges-preferred/358937#358937

# FIXME: Actual downloading of assets (`asset` variable should be changed!)

def _enumerate_xml_namespaces(state):
    stack = [state.xml.documentElement]
    while stack:
        v = stack.pop()
        for w in v.childNodes:
            yield w.namespaceURI
            stack.append(w)

@dataclass(order=True)
class PrioritizedNS:
    priority: int
    ns: Any=field(compare=False)


# Return a pair (priority, namespace)
def _enumerate_child_namespaces(state, asset):
    priority = 0
    yield from [PrioritizedNS(priority, ns) for ns in _enumerate_xml_namespaces(state)]
    for order_part in state.opts.recursiveOptions:
        priority += 1
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
            yield from [PrioritizedNS(priority, ns) for ns in state.opts.targetNamespaces]


def _enumerate_child_namespaces_without_priority(state, asset):
    return [x.ns for x in _enumerate_child_namespaces(state, asset)]


# Recursive algorithm for simplicity
def depth_first_download(state, asset, discovered):
    yield asset
    discovered.add(asset)
    for ns in _enumerate_child_namespaces_without_priority(state, asset):
        if ns not in discovered:
            depth_first_download(state, ns, discovered)  # recursion


def our_depth_first_based_download(state):
    for asset in state.opts.initial_assets:
        yield asset
    for asset in state.opts.initial_assets:
        iter = depth_first_download(state, asset, set(state.opts.initial_assets))
        next(iter)  # do not repeat the above
        yield from iter
