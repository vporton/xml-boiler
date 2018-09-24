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

# This is a wrapper above OS distribution version code.
# This file supports .* at the end of version number and infinite versions

from functools import total_ordering


# For "X.*" at the end of version see
# https://en.wikiversity.org/wiki/Automatic_transformation_of_XML_namespaces/RDF_resource_format

# WARNING: Comparison like like y.n > x.* does not work
# (we never compare it, because x.* can be only the upper bound not lower)
@total_ordering
class VersionWrapper(object):
    def __init__(self, version_class, version):
        """
        :param version: _Version() object
        """
        self.version_class = version_class
        self.version = version  # a string or float("inf") or float("-inf")

    def __eq__(self, other):
        return self.version == other.version

    def __ge__(self, other):
        if self.version == float("inf"):
            return True
        if self.version == float("-inf"):
            return other == float("-inf")  # never met in practice but check for completeness

        # x.* > x.n is the only special case for .*
        # (we never compare like y.n > x.*)

        if self.version == other.version:  # encompasses the case if both end with .*
            return True
        # Check the only special case when both start with the same prefix
        if self.version is str and self.version[-2:] == '.*' and \
                other.startswith(self.version[:-2] + '.'):
            return True
        version2 = self.version[:-2] if self.version[-2:] == '.*' else self.version
        return self.version_class(version2) >= self.version_class(other.version)

    def __str__(self):
        return self.version

    def __repr__(self):
        return "VersionWrapper(%s)" % self.version


def version_wrapper_create(version_class):
    def inner(version):
        return VersionWrapper(version_class, version)
    return inner