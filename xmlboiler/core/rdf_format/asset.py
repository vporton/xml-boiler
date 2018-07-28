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

from enum import Enum, auto
from typing import NamedTuple, Optional, AbstractSet, List

from rdflib import URIRef

from xmlboiler.core.graph.relation import BinaryRelation
from xmlboiler.core.graph.connect import Connectivity


class ScriptKindEnum(Enum):
    TRANSFORMER = auto()
    VALIDATOR   = auto()

class TransformerKindEnum(Enum):
    ENTIRE     = auto()
    SEQUENTIAL = auto()
    UP_DOWN    = auto()
    DOWN_UP    = auto()

class ValidatorKindEnum(Enum):
    ENTIRE = auto()
    PARTS  = auto()

# TODO: Distinguishing transformer and validator scripts does not conform to the specification
class BaseScriptInfo(NamedTuple):
    preservance : float
    stability   : float
    preference  : float
    script_kind: ScriptKindEnum
    transformer_kind: TransformerKindEnum
    validator_kind  : ValidatorKindEnum
    okResult: Optional[str]

class CommandScriptInfo(NamedTuple):
    language: URIRef
    min_version: Optional[str]
    max_version: Optional[str]
    # either one of the following must be None
    command_string: Optional[str]
    script_URL    : Optional[str]
    params: list

class WebServiceScriptInfo(NamedTuple):
    action: URIRef
    method: str
    xml_field: str

class ScriptInfo(NamedTuple):
    base: BaseScriptInfo
    more: NamedTuple

class Transformer(NamedTuple):
    source_namespaces: AbstractSet[URIRef]
    target_namespaces: AbstractSet[URIRef]
    ignore_target: bool
    precedence: Optional[URIRef]
    inwardness: Optional[bool]
    scripts: List[ScriptInfo]

class Namespace(NamedTuple):
    resource: URIRef
    validators: List[ScriptInfo]

class AssetInfo(NamedTuple):
    transformers: List[Transformer]
    namespaces  : List[Namespace]
    see_also_transform: List[URIRef]
    see_also_validate : List[URIRef]
    precedences_subclasses: BinaryRelation
    precedences_higher    : BinaryRelation
