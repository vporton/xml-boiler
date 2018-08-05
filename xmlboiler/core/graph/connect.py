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


from xmlboiler.core.graph.relation import union, square, BinaryRelation


def transitive_closure(graph):
    while True:
        result = union(graph, square(graph))
        if result == graph:
            return result
        graph = result


class Connectivity(object):
    def __init__(self):
        self.connectivity = BinaryRelation()

    def is_connected(self, src, dst):
        return src == dst or self.connectivity.adjanced(src, dst)

    def add_relation(self, relation):
        self.connectivity = transitive_closure(union(self.connectivity, relation))
