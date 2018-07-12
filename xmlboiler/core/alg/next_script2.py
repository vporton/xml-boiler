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

# the second algorithm from https://en.wikiversity.org/wiki/Automatic_transformation_of_XML_namespaces/Transformations/Automatic_transformation

# import networkx as nx
from .next_script_base import ScriptsIteratorBase


class ScriptsIterator(ScriptsIteratorBase):
    def __next__(self):
        next_outer = self._next_outer_script()
        if next_outer is not None:
            return next_outer

        pass  # TODO

    def _get_ns(self, node):
        if node.namespaceURI:
            result = [node.namespaceURI]
        else:
            result = []
        attr_nodes = [node[i] for i in range(node.length) if node[i].namespaceURI is not None]
        result.extend(sorted(set(attr_nodes)))  # set() to avoid repetitions
        return result

    def _outer_node_script(self, node):
        NSs = self._get_ns(node)  # TODO: May be inefficient to consider all these namespaces
        if not NSs:
            return None
        scripts = []
        for s in self.state.scripts:
            if NSs[0] in s.transformer.source_namespaces:
                scripts.append(s)
        return self._checked_scripts(scripts)