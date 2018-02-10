import os
import pkg_resources

class Global:
    @staticmethod
    def get_resource(filename):
        if os.environ.get('XMLBOILER_PATH', "") != "":
            return open(os.environ['XMLBOILER_PATH'] + '/' + filename, 'r')
        else:
            return pkg_resources.resource_stream('xmlboiler', filename)
