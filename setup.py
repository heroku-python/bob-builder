#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys

from setuptools import setup

deps = [
    'boto',
    'docopt',
    'envoy'
]

setup(
    name='bob-builder',
    version='0.0.12',
    install_requires=deps,
    description='Binary Build Toolkit.',
    # long_description='Meh.',/
    author='Kenneth Reitz',
    author_email='kenneth@heroku.com',
    url='https://github.com/kennethreitz/bob-builder',
    packages=['bob'],
    license='MIT',
    entry_points={
        'console_scripts': [
            'bob = bob:cli.dispatch',
        ],
    }
)
