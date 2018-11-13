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
import urllib  # very poor functionality, should probably be replaced with another module
import urllib.request
from dependency_injector import providers, containers
import xmlboiler.core.data


def _local_url_to_file(url):
    return re.sub(r'(?i)^local:', '', url)


class _local_handler(urllib.request.BaseHandler):
    def local_open(req):
        filename = _local_url_to_file(req.get_full_url())
        return xmlboiler.Global.get_resource_stream(filename)


def _build_opener():
    # Note that it adds HTTP and other handlers automatically
    return urllib.request.build_opener(_local_handler)

class MyOpener(object):
    def __init__(self, opener, timeout):
        self.opener = opener
        self.timeout = timeout

    def open(self, *args, **kwargs):
        return self.opener.open(*args, timeout=self.timeout, **kwargs)


class CannotConvertURLToLocalFile(RuntimeError):
    def __repr__(self):
        return "Cannot convert URL to local file"


def _url_to_file(url):
    filename = _local_url_to_file(url)
    if filename != url:  # substitution happened
        return xmlboiler.core.data.Global.get_filename('core/data/'+filename)
    if re.match(r'(?i)^file:', url):
        return urllib.request.url2pathname(urllib.parse.urlparse(url).path)
    raise CannotConvertURLToLocalFile()


class OurOpeners(containers.DeclarativeContainer):
    _our_opener = providers.ThreadSafeSingleton(_build_opener)
    our_opener = providers.ThreadSafeSingleton(MyOpener, opener=_our_opener, timeout=10.0)
    url_to_file = _url_to_file
