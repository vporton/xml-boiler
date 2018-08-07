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
from typing import Set, FrozenSet, List, Optional

import xml.dom.minidom
from rdflib import URIRef
from rdflib.resource import Resource

from xmlboiler.core.graph.connect import Connectivity
from xmlboiler.core.options import TransformationAutomaticWorkflowElementOptions
from xmlboiler.core.rdf_format.asset import ScriptInfo, Transformer


@dataclass
class EnrichedScript(object):
    script: ScriptInfo = None
    transformer: Transformer = None


@dataclass
class BaseState(object):
    opts: TransformationAutomaticWorkflowElementOptions
    xml_text: bytes = None
    assets: Set[Resource] = field(default_factory=set)


@dataclass
class PipelineState(BaseState):
    dom: Optional[xml.dom.minidom.Document] = None
    all_namespaces: Optional[FrozenSet[URIRef]] = None
    scripts: List[EnrichedScript] = field(default_factory=list)
    executed_scripts: Set[EnrichedScript] = field(default_factory=set)  # TODO: Should be a set/frozenset?
    failed_scripts: Set[EnrichedScript] = field(default_factory=set)
    singletons: Set[URIRef] = field(default_factory=set)
    precedences_higher: Connectivity = field(default_factory=Connectivity)
    precedences_subclasses: Connectivity = field(default_factory=Connectivity)

    def add_asset(self, asset):
        self.scripts += [script for transformer in asset.transformers for script in transformer.scripts]
        # TODO: Don't use private field .connectivity
        self.precedences_higher.add_relation(asset.precedences_higher.connectivity)
        self.precedences_subclasses.add_relation(asset.precedences_subclasses.connectivity)
