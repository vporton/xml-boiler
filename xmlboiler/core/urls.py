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

# TODO: Support configuring proxies, timeouts, etc.

# TODO: correct module is urllib or urllib2?
import re
import urllib
from dependency_injector import providers, containers
import xmlboiler.core.data

class _local_handler(urllib.request.BaseHandler):
    def local_open(req):
        # TODO: Some code duplication with the below
        filename = re.sub(r'(?i)^local:', '', req.get_full_url())
        return xmlboiler.Global.get_resource_stream(filename)


def _build_opener():
    # Note that it adds HTTP and other handlers automatically
    return urllib.request.build_opener(_local_handler)


class CannotConvertURLToLocalFile(RuntimeError):
    def __repr__(self):
        return "Cannot convert URL to local file"


def _url_to_file(url):
    # TODO: Some code duplication with the above
    filename = re.sub(r'(?i)^local:', '', url)
    if filename != url:  # substitution happened
        return xmlboiler.core.data.Global.get_filename('core/data/'+filename)
    filename = re.sub(r'(?i)^file:///?', '', url)
    if filename != url:
        return '/' + filename  # TODO: Windows support
    raise CannotConvertURLToLocalFile()


# TODO: Use dependency injectors instead of this global object
class OurOpeners(containers.DeclarativeContainer):
    opener = providers.ThreadSafeSingleton(_build_opener)
    url_to_file = _url_to_file
