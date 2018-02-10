from typing import NamedTuple
from enum import Enum, auto
from ordered_set import OrderedSet


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
