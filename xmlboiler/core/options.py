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
from logging import Logger
from typing import Optional, Callable, List, Any
from enum import Enum, auto
from ordered_set import OrderedSet

from rdflib import URIRef, Graph

### Base ###
# from xmlboiler.core.alg.next_script_base import ScriptsIteratorBase
from xmlboiler.core.execution_context import ExecutionContext
from xmlboiler.core.os_command.base import BaseCommandRunner
from xmlboiler.core.packages.base import BasePackageManaging
from xmlboiler.core.urls import MyOpener


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
    downloaders: List[List[Callable[[URIRef], Graph]]] = None
    initial_assets: OrderedSet = None  # OrderedSet[URIRef]  # downloaded before the main loop
    recursive_download: RecursiveDownload = None
    retrieval_priority: RecursiveRetrievalPriority = None


@dataclass
class InstalledSoftwareOptions(object):
    package_manager: BasePackageManaging = None  # None means not to use package_manager
    use_path: bool = True


# In this version the same options are applied to all elements of the
# workflow, but in future we may increase "granularity" to have different
# options for different elements.
@dataclass
class BaseAlgorithmOptions(object):
    execution_context: ExecutionContext = None
    error_logger: Logger = None  # may be stderr
    command_runner: BaseCommandRunner = None
    url_opener: MyOpener = None
    # kind: WorklowKind = None
    recursive_options: RecursiveDownloadOptions = RecursiveDownloadOptions()
    installed_soft_options: InstalledSoftwareOptions = InstalledSoftwareOptions()

    weight_formula: str = None

    def my_deepcopy(self):
        return BaseAlgorithmOptions(execution_context=self.execution_context,
                                    error_logger=self.error_logger,
                                    command_runner=self.command_runner,
                                    url_opener=self.url_opener,
                                    recursive_options=self.recursive_options,
                                    installed_soft_options=self.installed_soft_options,
                                    weight_formula=self.weight_formula)


class NotInTargetNamespace(Enum):
    IGNORE = auto()
    REMOVE = auto()  # TODO: Not implemented
    ERROR  = auto()


@dataclass
class BaseAutomaticWorkflowElementOptions(object):
    algorithm_options: BaseAlgorithmOptions = None
    not_in_target: NotInTargetNamespace = None

    # quick hack
    def __getattr__(self, attr):
        return getattr(self.algorithm_options, attr)

### Validation ###

class ValidationOrderType(Enum):
    DEPTH_FIRST   = auto()
    BREADTH_FIRST = auto()

@dataclass
class ValidationAutomaticWorkflowElementOptions(BaseAutomaticWorkflowElementOptions):
    validation_order: ValidationOrderType = None
    unknown_namespaces_is_invalid: bool = None

### Transformation ###

@dataclass
class ChainOptions(object):
    """For `chain` command."""
    # __slots__ = 'element_options', 'next_script', 'universal_precedence', 'target_namespaces'
    element_options: BaseAutomaticWorkflowElementOptions = None
    universal_precedence: Optional[URIRef] = None  # TODO: Find a better name for this option
    target_namespaces: frozenset = None  # frozenset[URIRef]

    # quick hack
    def __getattr__(self, attr):
        return getattr(self.element_options, attr)


@dataclass
class ScriptOptions(object):
    """For `script` command."""
    element_options: BaseAutomaticWorkflowElementOptions = None
    script_url: URIRef = None

    # quick hack
    def __getattr__(self, attr):
        return getattr(self.element_options, attr)


@dataclass
class TransformOptions(object):
    """For `script` command."""
    element_options: BaseAutomaticWorkflowElementOptions = None
    transform_url: URIRef = None

    # quick hack
    def __getattr__(self, attr):
        return getattr(self.element_options, attr)


@dataclass
class PipelineOptions(object):
    """For `pipe` command."""
    # __slots__ = 'element_options', 'next_script', 'universal_precedence', 'target_namespaces'
    element_options: BaseAutomaticWorkflowElementOptions = None

    # quick hack
    def __getattr__(self, attr):
        return getattr(self.element_options, attr)
