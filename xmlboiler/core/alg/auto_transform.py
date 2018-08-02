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

from xmlboiler.core.alg.common import RealNextScript


class AutomaticTranformation(object):
    def __init__(self, state):
        state.dom = parseString(state.xml_text)
        self.state = state
        self.state.next_asset = self.state.opts.recursive_options.download_algorithm

    def _step(self):
        all_namespaces = set()

        # depth-first search
        parents = [self.state.dom.documentElement]
        while parents:
            v = parents.pop()
            if v.namespaceURI is not None:
                all_namespaces.append(v.namespaceURI)
            for w in v.childNodes:
                parents.append(w)

        self.state.all_namespaces = frozenset(all_namespaces)  # TODO: Is it worth to freeze?

        if self.state.all_namespaces <= self.state.opts.target_namespaces:
            return False  # The transformation finished!

        try:
            RealNextScript(self.state).step()
        except StopIteration:
            # may propagate one more StopIteration, exiting from the main loop
            next(self.state.next_asset)

        return True

    def run(self):
        self.state.dom = parseString(self.state.xml_text)
        while self._step():  # may raise StopIteration
            pass
