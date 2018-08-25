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
from enum import Enum, auto
from typing import Optional, AbstractSet, List, Any

from rdflib import URIRef

from xmlboiler.core.graph.relation import BinaryRelation
# from xmlboiler.core.graph.connect import Connectivity


class ScriptKindEnum(Enum):
    TRANSFORMER = auto()
    VALIDATOR   = auto()

class TransformerKindEnum(Enum):
    ENTIRE = auto()
    SIMPLE_SEQUENTIAL = auto()
    SUBDOCUMENT_SEQUENTIAL = auto()
    DOWN_UP = auto()
    PLAIN_TEXT = auto()

class ValidatorKindEnum(Enum):
    ENTIRE = auto()
    PARTS  = auto()

# TODO: Distinguishing transformer and validator scripts does not conform to the specification
@dataclass
class BaseScriptInfo(object):
    transformer: Any #Transformer
    script_kind: ScriptKindEnum
    preservance : float = None
    stability   : float = None
    preference  : float = None
    transformer_kind: TransformerKindEnum = None
    validator_kind  : ValidatorKindEnum = None
    ok_result: Optional[str] = None

@dataclass
class CommandScriptInfo(object):
    language: URIRef = None
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    # either one of the following must be None
    command_string: Optional[str] = None
    script_url    : Optional[str] = None
    params: list = field(default_factory=list)

@dataclass
class WebServiceScriptInfo(object):
    action: URIRef = None
    method: str = None
    xml_field: str = None

@dataclass
class ScriptInfo(object):
    base: BaseScriptInfo = None
    more: object = None

    def __hash__(self):
        return id(self)

@dataclass
class Transformer(object):
    source_namespaces: AbstractSet[URIRef] = None
    target_namespaces: AbstractSet[URIRef] = None
    ignore_target: bool = False
    precedence: Optional[URIRef] = None
    inwardness: Optional[bool] = None
    scripts: List[ScriptInfo] = None

@dataclass
class Namespace(object):
    resource: URIRef
    validators: List[ScriptInfo]

@dataclass
class AssetInfo(object):
    transformers: List[Transformer] = field(default_factory=list)
    namespaces  : List[Namespace] = field(default_factory=list)
    see_also_transform: List[URIRef] = field(default_factory=list)
    see_also_validate : List[URIRef] = field(default_factory=list)
    precedences_subclasses: BinaryRelation = None
    precedences_higher    : BinaryRelation = None
