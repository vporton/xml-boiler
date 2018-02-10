#  Copyright (c) 2017 Victor Porton,
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


from rdflib import URIRef

from xmlboiler.core.graph.base import BinaryRelation
from xmlboiler.core.graph.connect import Connectivity
from xmlboiler.core.execution_context_builders import Contexts


class SubclassRelation(Connectivity):
    def __init__(self,
                 context=Contexts.execution_context(),
                 model=None,
                 relation=URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf")):
        self.context = context
        self.relation = relation
        self.add_model(model)

    def add_model(self, model):
        result = BinaryRelation()
        were_errors = False
        for subject, object in model[:self.relation]:
             if object is URIRef:
                 if self.check_types(model, subject, object):
                     result.add_edge(subject, object)
             else:
                 were_errors = True
                 msg = self.context.translations.gettext("Node %s should be an IRI." % str(object))
                 self.context.logger.warning(msg)
        self.add_relation(result)
        return not were_errors

    def check_types(self, model, src, dst):
        return True