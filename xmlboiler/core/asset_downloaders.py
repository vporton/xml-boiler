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


# Currently (for security reasons as our Firejail is not yet secure)
# we support only one method of downloading assets for a given URL:
# we use a local file named after the URL.

import urllib.parse

import rdflib

import xmlboiler.core.data


def directory_asset_downloader(dir):
    def downloader(url):
        try:
            with open(dir + '/' + urllib.parse.quote(url, safe=''), 'r') as file:
                g = rdflib.Graph()
                g.load(file)
        except FileNotFoundError:
            return None
        return g
    return downloader


# No need to be dependency injected, because it is to be used only in initialization code.
def local_asset_downloader(url):
    try:
        return xmlboiler.core.data.Global.load_rdf('core/data/assets/' + urllib.parse.quote(url, safe=''))
    except FileNotFoundError:
        return None
