from coverage.annotate import os
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as DistutilsBuild


class MyBuild(DistutilsBuild):
    def run(self):
        DistutilsBuild.run(self)
        os.system('make')


setup(
    name='xml-boiler',
    version='0.0.1',
    url='https://github.com/vporton/xml-boiler',
    license='AGPLv3',
    author='Victor Porton',
    author_email='porton@narod.ru',
    description='Automatically transform between XML namespaces',

    packages=find_packages(),
    package_data={'': ['*.ttl', '*.xml']},
    scripts=['bin/boiler'],
    data_files = [
        ('/etc/xmlboiler', ['etc/config-cli.ttl'])
    ],
    test_suite="xmlboiler.tests",

    cmdclass={'build_py': MyBuild},
)
