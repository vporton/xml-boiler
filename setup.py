from coverage.annotate import os
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as DistutilsBuild


class MyBuild(DistutilsBuild):
    def run(self):
        DistutilsBuild.run(self)
        os.system('make')


setup(
    name='xml-boiler',
    version='0.2.5',
    url='https://github.com/vporton/xml-boiler',
    license='AGPLv3',
    author='Victor Porton',
    author_email='porton@narod.ru',
    description='Automatically transform between XML namespaces',
    keywords='XML,XML namespaces,file format conversion',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: XML',
    ],

    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages(),
    # package_data={'': ['**/*.xml', '**/*.ttl', '**/*.net', 'data/assets/*', 'data/scripts/*.xslt',
    #                    'xmlboiler/doc/*.html', 'xmlboiler/doc/*.css']},
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/boiler'],
    # Does not work for non-root install:
    # data_files = [
    #     ('/etc/xmlboiler', ['etc/config-cli.ttl'])
    # ],
    test_suite="xmlboiler.tests",

    cmdclass={'build_py': MyBuild},
)
