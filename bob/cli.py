# -*- coding: utf-8 -*-

"""Usage: bob build <formula>
       bob deploy <formula>

Build formula and optionally deploy it.

Options:
    -h --help
    --no-deps  skip dependency cascading.

Configuration:
    Environment Variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET
"""
import os

from docopt import docopt
from .models import Formula



def build(formula):

    f = Formula(path=formula)

    try:
        assert f.exists
    except AssertionError:
        print 'Formula {} doesn\'t appear to exist.'.format(formula)
        exit(1)

    print 'Building {}'.format(formula)

    # Dependency metadata, extracted from bash comments.
    deps = f.depends_on
    print

    if deps:
        print 'Resolving dependencies... found {}:'.format(len(deps))

        for dep in deps:
            print '  - {}'.format(dep)

    print

    # CLI lies ahead.
    f.build()

    return f

    # Tarball
    # Upload to an s3 bucket
    # Then, sidestep.


def deploy(formula):
    f = build(formula)

    print 'Build successful.'
    print 'Archiving.'
    f.archive()

    print 'Deploying.'
    f.deploy()



def dispatch():

    args = docopt(__doc__)

    formula = args['<formula>']
    do_build = args['build']
    do_deploy = args['deploy']

    if do_build:
        build(formula)

    if do_deploy:
        deploy(formula)
