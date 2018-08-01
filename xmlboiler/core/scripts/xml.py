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

from xmlboiler.core.rdf_format.asset import TransformerKindEnum


class XMLRunCommandWrapper(object):
    def __init__(self, script, kind):
        self.script = script
        self.kind = kind

    def run(self, input: bytes) -> bytes:
        map = {
            TransformerKindEnum.ENTIRE: self._run_entire,
            TransformerKindEnum.SIMPLE_SEQUENTIAL: self._run_simple_seq,
            TransformerKindEnum.SUBDOCUMENT_SEQUENTIAL: self._run_subdoc_seq,
            TransformerKindEnum.DOWN_UP: self._run_down_up,
        }
        return map[self.kind](input)

    def _run_entire(self, input: bytes) -> bytes:
        return self.script.run(input)

    def _run_simple_seq(self, input: bytes) -> bytes:
        while True:
            doc = parseString(input)
            # depth-first search
            parents = [doc.documentElement]
            found = False
            while parents and not found:
                v = parents.pop()
                for w in v.childNodes:
                    if w.namespaceURI in self.script.transformer.source_namespaces:
                        found = True
                        break
                    else:
                        # TODO: https://bugs.python.org/issue34306
                        if any(a.namespaceURI in self.script.transformer.source_namespaces for a in w.attributes.values()):
                            found = True
                            break
                    parents.append(w)
            if not found:
                return input  # TODO: Check XML validity? (point this in the specification)
            input = self.script.run(input)

    def _run_subdoc_seq(self, input: bytes) -> bytes:
        doc = parseString(input)
        # depth-first search
        parents = [doc.documentElement]
        while parents:
            v = parents.pop()
            for w in v.childNodes:
                if w.namespaceURI in self.script.transformer.source_namespaces:
                    str = w.toxml()
                    str2 = self.script.run(str)
                    frag = parseString(str2)
                    v.replaceChild(w, frag.documentElement)  # It does not break the for-loop, because childNodes is "live"
                parents.append(w)
        return doc.toxml()

    # FIXME
    def _run_down_up(self, input: bytes) -> bytes:
        pass  # TODO

    # Should be moved to a more general class?
    def _is_primary_node(self, node):
        # TODO: https://bugs.python.org/issue34306
        if node.parentNode.parentNode is None:  # if parentNode is minidom.Document
            if node.namespaceURI in self.script.transformer.source_namespaces or \
                    any(a.namespaceURI in self.script.transformer.source_namespaces for a in node.attributes.values()):
                return True
            return False
        if node.namespaceURI != node.parentNode.namespaceURI and \
                node.namespaceURI in self.script.transformer.source_namespaces:
            return True
        return any(a.namespaceURI != node.namespaceURI and a.namespaceURI in self.script.transformer.source_namespaces \
                   for a in node.attributes.values())
