# -*- coding: utf-8 -*-

"""Usage: bob build <formula> [--name=FILE]
       bob deploy <formula> [--overwrite] [--name=<FILE>]

Build formula and optionally deploy it.

Options:
    -h --help
    --overwrite  allow overwriting of deployed archives.
    --name=<path>  allow separate name for the archived output

Configuration:
    Environment Variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET, S3_PREFIX (optional), UPSTREAM_S3_BUCKET (optional), UPSTREAM_S3_PREFIX (optional)
"""
from __future__ import print_function

import sys

from docopt import docopt
from .models import Formula
from .utils import print_stderr


def build(formula, name=None):
    f = Formula(path=formula, override_path=name)

    try:
        assert f.exists
    except AssertionError:
        print_stderr("Formula {} doesn't exist.".format(formula))
        sys.exit(1)

    # CLI lies ahead.
    f.build()

    return f


def deploy(formula, overwrite, name):
    f = build(formula, name)

    print('Archiving.')
    f.archive()

    print('Deploying.')
    f.deploy(allow_overwrite=overwrite)


def main():
    args = docopt(__doc__)

    formula = args['<formula>']
    do_build = args['build']
    do_deploy = args['deploy']
    do_overwrite = args['--overwrite']
    do_name = args['--name']

    if do_build:
        build(formula, name=do_name)

    if do_deploy:
        deploy(formula, overwrite=do_overwrite, name=do_name)


def dispatch():
    try:
        main()
    except KeyboardInterrupt:
        print('ool.')
        sys.exit(130)
