#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
import re
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'oculoenv'
DESCRIPTION = 'Oculomotor task environments.'
URL = 'https://github.com/wbap/oculoenv'
EMAIL = 'miyosuda@gmail.com'
AUTHOR = 'Whole Brain Architecture Initiative'
REQUIRES_PYTHON = '>=2.7.0'
VERSION = None

REQUIRED = ['pyglet', 'numpy']

EXTRAS = {}

here = os.path.abspath(os.path.dirname(__file__))

long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

# Collect data file pathes under 'oculoenv/data' as '###/*.*'
data_pathes = []
for root, folders, files in os.walk("oculoenv/data"):
    data_path = re.sub("\\\\", "/", re.sub("oculoenv/", "", root)) + "/*.*"
    data_pathes.append(data_path)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(
            sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests', )),
    package_data={'oculoenv': data_pathes},
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
