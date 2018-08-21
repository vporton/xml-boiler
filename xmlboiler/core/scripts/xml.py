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

from xmlboiler.core.rdf_format.asset import TransformerKindEnum

# TODO: Don't parse directly after serializing (for efficiency)
from xmlboiler.core.rdf_format.asset_parser.script import AttributeParam
from xmlboiler.core.scripts.text import RunCommand


class XMLRunCommandWrapper(object):
    """
    Don't use it directly, use XMLRunCommand
    """
    def __init__(self, script, kind, interpreters):
        self.script = script
        self.kind = kind
        self.interpreters = interpreters
        self.params = self.script.more.params

    def run(self, input: bytes) -> bytes:
        map = {
            TransformerKindEnum.ENTIRE: self._run_entire,
            TransformerKindEnum.SIMPLE_SEQUENTIAL: self._run_simple_seq,
            TransformerKindEnum.SUBDOCUMENT_SEQUENTIAL: self._run_subdoc_seq,
            TransformerKindEnum.DOWN_UP: self._run_down_up,
            TransformerKindEnum.PLAIN_TEXT: self._run_plain_text,
        }
        return map[self.kind](input)

    def _run_entire(self, input: bytes) -> bytes:
        return RunCommand(self.script, self.interpreters).run(input, self.params)

    def _run_simple_seq(self, input: bytes) -> bytes:
        while True:
            doc = parseString(input)
            # depth-first search (TODO: check the alg)
            parents = [doc.documentElement]
            found = False
            while parents and not found:
                v = parents.pop()
                for w in v.childNodes:
                    if URIRef(w.namespaceURI) in self.script.transformer.source_namespaces:
                        found = True
                        break
                    else:
                        # TODO: https://bugs.python.org/issue34306
                        if any(URIRef(a.namespaceURI) in self.script.transformer.source_namespaces for a in w.attributes.values()):
                            found = True
                            break
                    parents.append(w)
            if not found:
                return input  # TODO: Check XML validity? (point this in the specification)
            input = RunCommand(self.script, self.interpreters).run(input, self.params)

    def _run_subdoc_seq(self, input: bytes) -> bytes:
        doc = parseString(input)
        # depth-first search (TODO: check the alg)
        parents = [doc.documentElement]
        while parents:
            v = parents.pop()
            for w in v.childNodes:
                if URIRef(w.namespaceURI) in self.script.transformer.source_namespaces:
                    str = w.toxml('utf-8')
                    str2 = RunCommand(self.script, self.interpreters).run(str, self.adjust_params(w))
                    frag = parseString(str2)
                    v.replaceChild(w, frag.documentElement)
                parents.append(w)
        return doc.toxml('utf-8')

    def _run_down_up(self, input: bytes) -> bytes:
        while True:
            input = self._run_down_up_step(input)
            if input is None:
                return input

    def _run_down_up_step(self, input: bytes) -> bytes:
        doc = parseString(input)
        # depth-first search
        parents = [doc.documentElement]
        while parents:
            v = parents.pop()
            if not v.childNodes:
                for node in reversed(parents):
                    if self._is_primary_node(node):
                        str = node.toxml('utf-8')
                        str2 = RunCommand(self.script, self.interpreters).run(str, self.adjust_params(node))  # TODO: Don't run adjust_params() in  a loop
                        frag = parseString(str2)
                        node.parentNode.replaceChild(node, frag.documentElement)
                        return doc.toxml('utf-8')
            for w in v.childNodes:
                parents.append(w)
        return None

    def _run_plain_text(self, input: bytes) -> bytes:
        doc = parseString(input)
        our_elements = []
        # depth-first search
        parents = [doc.documentElement]
        while parents:
            v = parents.pop()
            if v.namespaceURI and URIRef(v.namespaceURI) in self.script.base.transformer.source_namespaces or \
                    (v.attributes and \
                     any(URIRef(a.namespaceURI) in self.script.base.transformer.source_namespaces for a in v.attributes.values() if a.namespaceURI)):
                if len(v.childNodes) > 1 or (len(v.childNodes) == 1 and v.childNodes[0].nodeType != v.childNodes[0].TEXT_NODE):
                    raise Exception("Non-text tag content in plain text transformer.")  # TODO: More specific exception
                our_elements.append((v, v.childNodes[0]))
            for w in v.childNodes:
                parents.append(w)

        for node, text in our_elements:
            # input = self._run_down_up_step(str(text).encode('utf-8'))
            input = RunCommand(self.script, self.interpreters).run(text.nodeValue.encode('utf-8'), self.adjust_params(node))
            doc2 = parseString(input)
            if node.namespaceURI and URIRef(node.namespaceURI) in self.script.base.transformer.source_namespaces:
                node.parentNode.replaceChild(doc2.documentElement, node)
            else:
                node.replaceChild(doc2.documentElement, node.firstChild)
                lst = list(node.attributes.values())  # "RuntimeError: dictionary changed size during iteration" without this
                for a in lst:
                    if URIRef(a.namespaceURI) in self.script.base.transformer.source_namespaces:
                        node.removeAttributeNS(a.namespaceURI, a.localName)

        return doc.toxml('utf-8')

    # Should be moved to a more general class?
    def _is_primary_node(self, node):
        # TODO: https://bugs.python.org/issue34306
        if node.parentNode.parentNode is None:  # if parentNode is minidom.Document
            if node.namespaceURI and URIRef(node.namespaceURI) in self.script.transformer.source_namespaces or \
                    any(URIRef(a.namespaceURI) in self.script.transformer.source_namespaces for a in node.attributes.values()):
                return True
            return False
        if node.namespaceURI != node.parentNode.namespaceURI and \
                URIRef(node.namespaceURI) in self.script.transformer.source_namespaces:
            return True
        return any(a.namespaceURI != node.namespaceURI and URIRef(a.namespaceURI) in self.script.transformer.source_namespaces \
                   for a in node.attributes.values())

    def adjust_params(self, node):
        result = []
        for p in self.script.more.params:
            p2 = p[1]
            if isinstance(p2, AttributeParam):
                result.append((p[0], node.getAttributeNS(str(p2.ns), p2.name)))  # TODO: Catch the exception
            else:
                result.append(p)
        return result


class XMLRunCommand(XMLRunCommandWrapper):
    def __init__(self, script, interpreters):
        super().__init__(script, script.base.transformer_kind, interpreters)
