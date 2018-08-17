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

from defusedxml.minidom import parseString
from rdflib import URIRef

from xmlboiler.core.alg.common import RealNextScript


class AssetsExhausted(StopIteration):
    pass


class AutomaticTranformation(object):
    def __init__(self, state, interpreters):
        state.dom = parseString(state.xml_text)
        self.state = state
        self.interpreters = interpreters
        self.state.next_asset = self.state.opts.recursive_options.download_algorithm

    def _step(self):
        all_namespaces = set()

        self.state.dom = parseString(self.state.xml_text)

        # depth-first search
        parents = [self.state.dom.documentElement]
        while parents:
            v = parents.pop()
            if v.namespaceURI is not None:
                all_namespaces.add(URIRef(v.namespaceURI))
            if v.attributes:
                for a in v.attributes.values():
                    if a.namespaceURI is not None:
                        all_namespaces.add(URIRef(a.namespaceURI))
            for w in v.childNodes:
                parents.append(w)

        # hack
        self.state.all_namespaces = frozenset(filter(lambda x: x != URIRef('http://www.w3.org/2000/xmlns/'), all_namespaces))  # TODO: Is it worth to freeze?

        if self.state.all_namespaces <= self.state.opts.target_namespaces:
            return False  # The transformation finished!

        try:
            RealNextScript(self.state, self.interpreters).step()
        except StopIteration:
            try:
                next(self.state.next_asset)
            except StopIteration:
                raise AssetsExhausted()

        return True

    def run(self):
        self.state.dom = parseString(self.state.xml_text)
        while self._step():  # may raise AssetsExhausted
            pass
