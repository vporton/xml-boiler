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
from dataclasses import dataclass
from typing import Optional, Callable, List, Any
from enum import Enum, auto
from ordered_set import OrderedSet

from rdflib import URIRef, Graph

### Base ###
# from xmlboiler.core.alg.next_script_base import ScriptsIteratorBase
from xmlboiler.core.execution_context import ExecutionContext
from xmlboiler.core.packages.base import BasePackageManaging


class WorklowKind(Enum):
    TRANSFORMATION = auto()
    VALIDATION     = auto()

class RecursiveDownload(Enum):
    NONE          = auto()
    DEPTH_FIRST   = auto()
    BREADTH_FIRST = auto()

class RecursiveRetrievalPriorityOrderElement(Enum):
    SOURCES = auto()
    TARGETS = auto()
    WORKFLOW_TARGETS = auto()

class RecursiveRetrievalPriority(OrderedSet):
    """
    Element are RecursiveRetrievalPriorityOrderElement

    TODO: very inefficient
    """
    pass

@dataclass
class RecursiveDownloadOptions(object):
    download_algorithm: Any = None  #BaseDownloadAlgorithm = None
    downloaders: List[List[Callable[[URIRef], Graph]]] = None
    initial_assets: OrderedSet = None  # OrderedSet[URIRef]  # downloaded before the main loop
    recursive_download: RecursiveDownload = None
    retrieval_priority: RecursiveRetrievalPriority = None


@dataclass
class InstalledSoftwareOptions(object):
    package_manager: BasePackageManaging = None  # None means not to use package_manager
    path: bool = True


# In this version the same options are applied to all elements of the
# workflow, but in future we may increase "granularity" to have different
# options for different elements.
@dataclass
class BaseAutomaticWorkflowElementOptions(object):
    execution_context: ExecutionContext = None
    kind: WorklowKind = None
    recursive_options: RecursiveDownloadOptions = RecursiveDownloadOptions()
    installed_soft_options: InstalledSoftwareOptions = InstalledSoftwareOptions()

### Validation ###

class ValidationOrderType(Enum):
    DEPTH_FIRST   = auto()
    BREADTH_FIRST = auto()

@dataclass
class ValidationAutomaticWorkflowElementOptions(BaseAutomaticWorkflowElementOptions):
    validation_order: ValidationOrderType = None
    unknown_namespaces_is_invalid: bool = None

### Transformation ###

class NotInTargetNamespace(Enum):
    IGNORE = auto()
    REMOVE = auto()  # TODO: Not implemented
    ERROR  = auto()

@dataclass
class TransformationAutomaticWorkflowElementOptions(BaseAutomaticWorkflowElementOptions):
    next_script: Any = None #ScriptsIteratorBase = None  # avoid circular dependency
    not_in_target_namespace: NotInTargetNamespace = None
    universal_precedence: Optional[URIRef] = None  # TODO: Find a better name for this option
    target_namespaces: frozenset = None  # frozenset[URIRef]
