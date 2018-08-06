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

import functools
import itertools
import math


def shortest_path_to_edges(graph, path, weight):
    r"""
    :param graph:
    :param path: a list of nodes
    :param weight: a function
    :return: a list of lists of edges
    """
    result = []
    for i in range(len(path) - 1):
        last_weight = math.inf
        last_edges = []
        for e in graph[path[i]][path[i+1]]:
            new_weight = weight(e)
            if new_weight < last_weight:
                last_edges = []
            if new_weight <= last_weight:
                last_weight = new_weight
                last_edges.append(e)
        result.append(last_edges)
    return result


def shortest_paths_to_edges(graph, paths, weight):
    r"""
    :param graph:
    :param paths: a list of lists of nodes
    :param weight: a function
    :return: a list of lists of edges
    """
    result = []
    last_weight = math.inf
    for path in paths:
        new_lists_of_edges = shortest_path_to_edges(graph, path, weight)
        for new_edges in new_lists_of_edges:
            new_weight = itertools.reduce(filter(weight, new_edges), 0)
            if new_weight < last_weight:
                result = []
            if new_weight <= last_weight:
                last_weight = new_weight
                result.append(new_edges)
    return result


def shortest_lists_of_edges(edges, weight):
    r"""
    :param graph:
    :param edges: a list of lists of edges
    :param weight: a function
    :return: a list of lists of edges
    """
    result = []
    last_weight = math.inf
    for cur_edges in edges:
        new_weight = functools.reduce(filter(weight, cur_edges), 0)
        if new_weight < last_weight:
            result = []
        if new_weight <= last_weight:
            last_weight = new_weight
            result.append(cur_edges)
    return result
