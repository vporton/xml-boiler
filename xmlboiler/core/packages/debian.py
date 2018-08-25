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

import re
import deb_pkg_tools.utils
import deb_pkg_tools.version

from .base import BasePackageManaging


class DebianPackageManaging(BasePackageManaging):
    @classmethod
    def determine_package_version(cls, package_name):
        version = deb_pkg_tools.utils.find_installed_version(package_name)
        if version is None:
            return None
        # https://www.debian.org/doc/debian-policy/#s-f-version
        version = re.match(r'^([0-9]+:)?(.*)(-[a-zA-Z0-9+.~]+)?$', version)[2]
        return version

    VersionClass = deb_pkg_tools.version.Version
