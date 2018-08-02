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
from dataclasses import dataclass, field
from typing import NamedTuple, Set, FrozenSet, List, Optional

import xml.dom.minidom
from rdflib import URIRef
from rdflib.resource import Resource

from xmlboiler.core.graph.connect import Connectivity
from xmlboiler.core.graph.relation import BinaryRelation
from xmlboiler.core.options import TransformationAutomaticWorkflowElementOptions
from xmlboiler.core.rdf_format.asset import ScriptInfo, Transformer


class EnrichedScript(NamedTuple):
    script: ScriptInfo
    transformer: Transformer


@dataclass
class BaseState(object):
    opts: TransformationAutomaticWorkflowElementOptions
    xml_text: bytes
    assets: Set[Resource] = field(default_factory=set)


@dataclass
class PipelineState(BaseState):
    dom: Optional[xml.dom.minidom.Document] = None
    all_namespaces: Optional[FrozenSet[URIRef]] = None
    scripts: List[EnrichedScript] = field(default_factory=list)
    executed_scripts: Set[EnrichedScript] = field(default_factory=set)  # TODO: Should be a set/frozenset?
    singletons: Set[URIRef] = field(default_factory=set)
    precedences_higher: Connectivity = field(default_factory=Connectivity)
    precedences_subclasses: Connectivity = field(default_factory=Connectivity)

    def add_asset(self, asset):
        self.scripts += [script for transformer in asset.transformers for script in transformer.scripts]
        self.precedences_higher.add_relation(asset.precedences_higher)
        self.precedences_subclasses.add_relation(asset.precedences_subclasses)
