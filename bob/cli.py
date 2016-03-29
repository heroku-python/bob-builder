# -*- coding: utf-8 -*-

"""Usage: bob build <formula>
       bob deploy <formula> [--overwrite]

Build formula and optionally deploy it.

Options:
    -h --help
    --overwrite  allow overwriting of deployed archives.

Configuration:
    Environment Variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET, S3_PREFIX (optional), UPSTREAM_S3_BUCKET (optional), UPSTREAM_S3_PREFIX (optional)
"""
import os
import sys

from docopt import docopt
from .models import Formula



def build(formula):

    f = Formula(path=formula)

    try:
        assert f.exists
    except AssertionError:
        print 'Formula {} doesn\'t appear to exist.'.format(formula)
        sys.exit(1)

    # CLI lies ahead.
    f.build()

    return f

    # Tarball
    # Upload to an s3 bucket
    # Then, sidestep.


def deploy(formula, overwrite):
    f = build(formula)

    print 'Archiving.'
    f.archive()

    print 'Deploying.'
    f.deploy(allow_overwrite=overwrite)



def main():

    args = docopt(__doc__)

    formula = args['<formula>']
    do_build = args['build']
    do_deploy = args['deploy']
    do_overwrite = args['--overwrite']


    if do_build:
        build(formula)

    if do_deploy:
        deploy(formula, overwrite=do_overwrite)


def dispatch():
    try:
        main()
    except KeyboardInterrupt:
        print 'ool.'
        sys.exit(130)
