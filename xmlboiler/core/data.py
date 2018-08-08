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


import os
import pkg_resources
import rdflib


class Global(object):
    @staticmethod
    def get_filename(filename):
        if os.environ.get('XMLBOILER_PATH', "") != "":
            return os.environ['XMLBOILER_PATH'] + '/' + filename
        else:
            return pkg_resources.resource_filename('xmlboiler', filename)

    @staticmethod
    def get_resource_stream(filename):
        if os.environ.get('XMLBOILER_PATH', "") != "":
            return open(os.environ['XMLBOILER_PATH'] + '/' + filename, 'r')
        else:
            return pkg_resources.resource_stream('xmlboiler', filename)

    @staticmethod
    def get_resource_bytes(filename):
        filename = Global.get_filename(filename)
        with open(filename, "rb") as file:
            return file.read()

    @staticmethod
    def load_rdf(filename):
        g = rdflib.Graph()
        with Global.get_resource_stream(filename) as stream:
            g.load(stream, format='turtle')
        return g
