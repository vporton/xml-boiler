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

from xmlboiler.core.alg.common import RealNextScript


class AutomaticTranformation(object):
    def __init__(self, state):
        self.state = state

    def _step(self):
        all_namespaces = set()

        # depth-first search
        parents = [self.state.xml.documentElement]
        while parents:
            v = parents.pop()
            if v.namespaceURI is not None:
                all_namespaces.append(v.namespaceURI)
            for w in v.childNodes:
                parents.append(w)

        self.state.all_namespaces = frozenset(all_namespaces)  # TODO: Is it worth to freeze?

        if self.state.all_namespaces <= self.state.opts.target_namespaces:
            return  # The transformation finished!

        try:
            RealNextScript(self.state).step()
        except StopIteration:
            # may propagate one more StopIteration, exiting from the main loop
            next(self.state.opts.next_asset)  # TODO: add next_asset field

    def run(self):
        while True:
            self._step()  # may raise StopIteration
