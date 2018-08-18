#!/usr/bin/env python

# distutils/setuptools install script for azure_cis_scanner
import os
from setuptools import setup, find_packages

# Package info
NAME = 'azure_cis_scanner'
ROOT = os.path.dirname(__file__)
VERSION = __import__(NAME).__version__

# Requirements
requirements = []
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')) as f:
    for r in f.readlines():
        requirements.append(r.strip())

try:
    import matplotlib
    print('matplotlib found.  Graphing supported')
except:
    print('matplotlib not installed.  Graphing not supported')

# Setup
setup(
    name=NAME,
    version=VERSION,
    description='Azure CIS Scanner for security',
    long_description=open('README.rst').read(),
    author='kesten broughton, tanner harper',
    author_email='kesten.broughton@praetorian.com',
    url='https://github.com/praetorian-inc/azure_cis_scanner',
    entry_points={
        'console_scripts': [
            'azscan = azure_cis_scanner.__main__:main',
            #'azscanRulesGenerator = azure_cis_scanner.__rules_generator__:main',
            #'azscanListAll = azure_cis_scanner.__listall__:main'
        ]
    },
    packages=[
        'azure_cis_scanner', 
        'azure_cis_scanner.modules',
        'report', 
    ],
    package_data={
        'azure_cis_scanner': [
            'requirements.txt',
            'cis_structure.yaml'
        ],
        'report': [
            'static/*.css',
            'templates/*.html',
            'requirements.txt'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license='GNU General Public License v2 (GPLv2)',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ],
    scripts=[
      'bin/azscanner',
      'bin/azscanner.bat'
    ]
)
