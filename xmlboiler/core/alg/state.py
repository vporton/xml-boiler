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
from typing import Set, FrozenSet, List, Optional, Any, Dict

import xml.dom.minidom
from rdflib import URIRef
from rdflib.resource import Resource

from xmlboiler.core.graph.connect import Connectivity
from xmlboiler.core.options import ChainOptions
from xmlboiler.core.rdf_format.asset import ScriptInfo, Transformer


@dataclass
class BaseState(object):
    opts: ChainOptions
    xml_text: bytes = None
    assets: Set[Resource] = field(default_factory=set)


@dataclass
class PipelineState(BaseState):
    dom: Optional[xml.dom.minidom.Document] = None
    all_namespaces: Optional[FrozenSet[URIRef]] = None
    scripts: List[ScriptInfo] = field(default_factory=list)
    executed_scripts: Set[ScriptInfo] = field(default_factory=set)
    scripts_hash: Dict[URIRef, ScriptInfo] = field(default_factory=dict)
    transformers_hash: Dict[URIRef, Transformer] = field(default_factory=dict)
    failed_scripts: Set[ScriptInfo] = field(default_factory=set)  # FIXME: Store IDs/URIs of the scripts not scripts themselves
    singletons: Set[URIRef] = field(default_factory=set)
    precedences_higher: Connectivity = field(default_factory=Connectivity)
    precedences_subclasses: Connectivity = field(default_factory=Connectivity)
    next_script: Any = None  # avoid circular dependency # ScriptsIteratorBase = None
    download_algorithm: Any = None  #BaseDownloadAlgorithm = None

    def add_asset(self, asset):
        self.scripts += [script for transformer in asset.transformers for script in transformer.scripts]
        for t in asset.transformers:
            if isinstance(t.ns, URIRef):
                self.transformers_hash.setdefault(t.ns, t)
            for s in t.scripts:
                if isinstance(s.base.ns, URIRef):
                    self.scripts_hash.setdefault(s.base.ns, s)
        self.precedences_higher.add_relation(asset.precedences_higher.connectivity)
        self.precedences_subclasses.add_relation(asset.precedences_subclasses.connectivity)
