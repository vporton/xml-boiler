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
import operator

from networkx import NetworkXNoPath


def shortest_path_to_edges(graph, path, weight):
    r"""
    :param graph:
    :param path: a list of nodes
    :param weight: a function
    :return: a list of lists of edges
    """
    result = []
    for i in range(len(path) - 1):
        shortest_edges = []  # shortest edges between path[i] and path[i+1]
        last_weight = math.inf  # minimum found weight between them
        for _, e in graph[path[i]][path[i + 1]].items():
            new_weight = weight(e['attr_dict'])
            if new_weight < last_weight:
                shortest_edges = []
                last_weight = new_weight
            if new_weight <= last_weight:
                shortest_edges.append(e['attr_dict'])
        result.append(shortest_edges)
    return result


def shortest_paths_to_edges(graph, paths, weight):
    r"""
    :param graph:
    :param paths: a list of lists of nodes (representing several possible pathes)
    :param weight: a function
    :return: a list of lists of edges (every of which is the shortest)
    """
    result = []
    last_weight = math.inf
    for path in paths:
        list_of_lists_of_edges = shortest_path_to_edges(graph, path, weight)
        one_of_the_ways = [lst[0] for lst in list_of_lists_of_edges]
        new_weight = functools.reduce(operator.add, map(weight, one_of_the_ways), 0)
        if new_weight < last_weight:
            result = []
            last_weight = new_weight
        if new_weight <= last_weight:
            result.extend(list_of_lists_of_edges)  # FIXME: Need to take product
    return result


def shortest_lists_of_edges(edges, weight):
    r"""
    :param edges: a list of lists of edges
    :param weight: a function
    :return: a list of lists of edges
    """
    result = []
    last_weight = math.inf
    try:
        for cur_edges in edges:
            new_weight = functools.reduce(operator.add, map(weight, cur_edges), 0)
            if new_weight < last_weight:
                result = []
            if new_weight <= last_weight:
                last_weight = new_weight
                result.append(cur_edges)
    except NetworkXNoPath:
        pass
    return result
