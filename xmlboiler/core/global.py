import os
import pkg_resources

class Global:
    def get_resource(self, filename):
        if os.environ.get('XMLBOILER_PATH', "") != "":
            return open(os.environ['XMLBOILER_PATH'] + '/' + filename, 'r')
        else:
            return pkg_resources.resource_stream('xmlboiler', filename)
