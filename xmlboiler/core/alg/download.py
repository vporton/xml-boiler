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

from xmlboiler.core.options import RecursiveRetrievalPriorityOrderElement


def _enumerate_xml_namespaces(state):
    stack = [state.xml.documentElement]
    while stack:
        v = stack.pop()
        for w in v.childNodes:
            yield w.namespaceURI
            stack.append(w)


def _enumerate_child_namespaces(state, asset):
    yield from _enumerate_xml_namespaces(state)
    for order_part in state.opts.recursiveOptions:
        if order_part == RecursiveRetrievalPriorityOrderElement.SOURCES:
            for t in asset.transformers:
                for s in t.source_namespaces:
                    yield s
        elif order_part == RecursiveRetrievalPriorityOrderElement.TARGETS:
            for t in asset.transformers:
                for s in t.target_namespaces:
                    yield s
        elif order_part == RecursiveRetrievalPriorityOrderElement.WORKFLOW_TARGETS:
            yield from state.opts.targetNamespaces
