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

import itertools
import math


def shortest_path_to_edges(path):
    TODO


def shortest_pathes_to_edges(pathes, weight):
    result = []
    last_weight = math.inf
    for path in pathes:
        new_lists_of_edges = shortest_path_to_edges(path)
        for new_edges in new_lists_of_edges:
            weight = itertools.reduce(filter(weight, new_edges), 0)
            if weight < last_weight:
                result = []
            if weight <= last_weight:
                last_weight = weight
                result.append(new_edges)
    return result
