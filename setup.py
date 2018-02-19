from setuptools import setup

setup(
    name='xml-boiler',
    version='0.0.1',
    url='https://github.com/vporton/xml-boiler',
    license='AGPLv3',
    author='Victor Porton',
    author_email='porton@narod.ru',
    description='Automatically transform between XML namespaces',

    packages = ['xmlboiler'],
    package_data={'xmlboiler': ['*.ttl']},
    test_suite="xmlboiler.tests",
)
