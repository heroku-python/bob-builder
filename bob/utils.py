# -*- coding: utf-8 -*-

import errno
import os
import re
import tarfile
from subprocess import Popen, PIPE, STDOUT

def iter_marker_lines(marker, formula, strip=True):
    """Extracts any markers from a given formula."""

    with open(formula) as f:
        for line in f:
            if line.startswith(marker):

                if strip:
                    line = line[len(marker):]
                    line = line.strip()

                yield line


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def process(cmd, cwd=None):
    """A simple wrapper around the subprocess module; stderr is redirected to stdout."""
    p = Popen(cmd, cwd=cwd, shell=False, stdout=PIPE, stderr=STDOUT)
    return p


def pipe(a, b, indent=True):
    """Pipes stream A to stream B, with optional indentation."""

    for line in iter(a.readline, b''):

        if indent:
            b.write('    ')

        b.write(line)


def archive_tree(dir, archive):
    """Creates a tar.gz archive from a given directory."""
    with tarfile.open(archive, 'w:gz') as tar:
        # do not tar.add(dir) with empty arcname, that will create a "/" entry and tar will complain when extracting
        for item in os.listdir(dir):
            tar.add(dir+"/"+item, arcname=item)

def extract_tree(archive, dir):
    """Extract tar.gz archive to a given directory."""
    with tarfile.open(archive, 'r:gz') as tar:
        tar.extractall(dir)
