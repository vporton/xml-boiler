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

from dependency_injector import containers, providers
from rdflib import URIRef, RDFS, RDF

from xmlboiler.core.data import Global
from xmlboiler.core.graph.relation import BinaryRelation
from xmlboiler.core.graph.connect import Connectivity
from xmlboiler.core.execution_context_builders import Contexts

class SubclassRelation(Connectivity):
    def __init__(self,
                 context=Contexts.execution_context(),
                 graph=None,
                 relation=RDFS.subClassOf):
        super().__init__()
        self.context = context
        self.relation = relation
        self.add_graph(graph)

    def add_graph(self, graph):
        result = BinaryRelation()
        were_errors = False
        for subject, object in graph[:self.relation]:
             if isinstance(object, URIRef):
                 if self.check_types(graph, subject, object):
                     result.add_edge(subject, object)
             else:
                 were_errors = True
                 msg = self.context.translations.gettext("Node {node} should be an IRI.").format(node=object)
                 self.context.logger.warning(msg)
        self.add_relation(result)
        return not were_errors

    def check_types(self, graph, src, dst):
        return True


class SubclassRelationForType(SubclassRelation):
    def __init__(self,
                 node_class,
                 context=Contexts.execution_context(),
                 graph=None,
                 relation=RDFS.subClassOf):
        super().__init__(context=context, graph=graph, relation=relation)
        self.node_class = node_class

    def check_types(self, graph, src, dst):
        src_ok = (src, RDF.type, self.node_class) in graph
        dst_ok = (dst, RDF.type, self.node_class) in graph
        if src_ok ^ dst_ok:
            msg = self.context.translations.gettext("Both operands should be of type {type}").format(type=self.node_class)
            self.context.logger.warning(msg)
        return src_ok and dst_ok


basic_subclasses_graph = providers.ThreadSafeSingleton(Global.load_rdf, filename='core/data/subclasses.ttl')


class SubclassContainers(containers.DeclarativeContainer):
    basic_subclasses = providers.ThreadSafeSingleton(SubclassRelation,
                                                     context=Contexts.execution_context(),
                                                     graph=basic_subclasses_graph)
