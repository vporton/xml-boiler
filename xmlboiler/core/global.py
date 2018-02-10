import os
import pkg_resources
import rdflib

class Global:
    @staticmethod
    def get_resource_stream(filename):
        if os.environ.get('XMLBOILER_PATH', "") != "":
            return open(os.environ['XMLBOILER_PATH'] + '/' + filename, 'r')
        else:
            return pkg_resources.resource_stream('xmlboiler', filename)

    @staticmethod
    def load_rdf(filename):
        g = rdflib.Graph()
        g.load(Global.get_resource_stream(filename), format='turtle')
        return g