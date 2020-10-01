#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

deps = [
    'boto',
    'docopt',
]

setup(
    name='bob-builder',
    version='0.0.19',
    install_requires=deps,
    description='Binary Build Toolkit.',
    # long_description='Meh.',/
    author='Heroku',
    author_email='cfaist@heroku.com',
    url='https://github.com/heroku-python/bob-builder',
    packages=['bob'],
    license='MIT',
    entry_points={
        'console_scripts': [
            'bob = bob:cli.dispatch',
        ],
    }
)
