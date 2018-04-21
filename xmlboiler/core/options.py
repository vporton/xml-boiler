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
from enum import Enum, auto
from ordered_set import OrderedSet

from rdflib import URIRef

### Base ###

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

class RecursiveRetrievalPriority(OrderedSet):
    """
    Element are RecursiveRetrievalPriorityOrderElement

    TODO: very inefficient
    """
    pass

class RecursiveDownloadOptions(NamedTuple):
    recursive_download: RecursiveDownload
    retrieval_priority: RecursiveRetrievalPriority

# In this version the same options are applied to all elements of the
# workflow, but in future we may increase "granularity" to have different
# options for different elements.
class BaseAutomaticWorkflowElementOptions(NamedTuple):
    kind: WorklowKind
    recursiveOptions: RecursiveDownloadOptions

### Validation ###

class ValidationOrderType(Enum):
    DEPTH_FIRST   = auto()
    BREADTH_FIRST = auto()

class ValidationAutomaticWorkflowElementOptions(BaseAutomaticWorkflowElementOptions):
    validationOrder: ValidationOrderType
    UnknownNamespacesIsInvalid: bool

### Transformation ###

class NotInTargetNamespace(Enum):
    IGNORE = auto()
    REMOVE = auto()
    ERROR  = auto()

class TransformationAutomaticWorkflowElementOptions(BaseAutomaticWorkflowElementOptions):
    notInTargetNamespace: NotInTargetNamespace
    universalPrecendence: URIRef  # TODO: Find a better name for this option
