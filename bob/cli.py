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
import os
import signal
import sys

from docopt import docopt
from .models import Formula
from .utils import print_stderr


def build(formula, name=None):
    f = Formula(path=formula, override_path=name)

    try:
        assert f.exists
    except AssertionError:
        print_stderr("Formula {} doesn't exist.".format(formula), title='ERROR')
        sys.exit(1)

    # CLI lies ahead.
    f.build()

    return f


def deploy(formula, overwrite, name):
    f = build(formula, name)

    print_stderr('Archiving.')
    f.archive()

    print_stderr('Deploying.')
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


def sigint_handler(signo, frame):
    # when receiving a signal, a process must kill itself using the same signal
    # sys.exit()ing 0, 1, 130, whatever will not signal to the calling program that we terminated in response to the signal
    # best example: `for f in a b c; do bob deploy $f; done`, hitting Ctrl+C should interrupt Bob and stop the bash loop
    # that's only possible if Bash knows that we exited in response to Ctrl+C (=SIGINT), then it'll also terminate the loop
    # bash will report the exit status as 128+$signal, so 130 for SIGINT, but sys.exit(130) does not to the same thing - the value of 130 is simply bash's representation
    # killing ourselves with the signal number that we are aborting in response to does all this correctly, and bash will see the right WIFSIGNALED() status of our program, not WIFEXITED()
    
    # and finally, before we send ourselves the right signal, we must first restore the handler for it to the default
    signal.signal(signo, signal.SIG_DFL)
    os.kill(os.getpid(), signo)

def dispatch():
    signal.signal(signal.SIGINT, sigint_handler)
    main()
