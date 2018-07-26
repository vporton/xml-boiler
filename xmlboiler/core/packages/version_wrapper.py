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

from xmlboiler.core.packages.base import ThePackageManaging

_Version = ThePackageManaging.VersionClass

@total_ordering
class VersionWrapper(object):
    def __init__(self, version):
        self.version = version  # a string or float("inf") or float("-inf")

    def __ge__(self, other):
        if self.version == float("inf"):
            return True
        if self.version == float("-inf"):
            return other == float("-inf")  # never met in practice but check for completeness
        # FIXME: What if other[-2:] == '.*'?
        if self.version is str and self.version[-2:] == '.*':
            if _Version(self.version[:-2]) < _Version(other) and \
                    not other.startswith(self.version[:-2] + '.'):
                return False
        return _Version(self.version) >= _Version(other)
