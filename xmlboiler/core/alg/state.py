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

from typing import NamedTuple

import defusedxml
from rdflib import URIRef
from rdflib.resource import Resource

from xmlboiler.core.graph.relation import BinaryRelation
from xmlboiler.core.options import TransformationAutomaticWorkflowElementOptions
from xmlboiler.core.rdf_format.asset import ScriptInfo, Transformer


class EnrichedScript(NamedTuple):
    script: ScriptInfo
    transformer: Transformer


class BaseState(object):
    opts: TransformationAutomaticWorkflowElementOptions
    assets: set[Resource]
    xml: bytes
    graph: BinaryRelation[URIRef]


class PipelineState(BaseState):
    xml: defusedxml.minidom
    all_namespaces: frozenset[URIRef]
    scripts: list[EnrichedScript]
    executed_scripts: set[EnrichedScript]  # TODO: Should be a set/frozenset?
    singletons: set(URIRef)
    precedences_higher: BinaryRelation
    precedences_subclasses: BinaryRelation

    def add_asset(self, asset):
        self.scripts += [script for transformer in asset.transformers for script in transformer.scripts]
        # TODO
