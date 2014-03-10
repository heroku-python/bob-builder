# -*- coding: utf-8 -*-

import os
import re
import tarfile
from subprocess import Popen, PIPE


DEPENDS_MARKER = '# Build Deps: '
BUILD_PATH_MARKER = '# Build Path: '


def deps_extract(path):
    """Extracts a list of declared dependencies from a given formula."""

    depends = []

    with open(path) as f:
        for line in f:
            # Depends: libraries/libsqlite, libraries/libsqlite
            if line.startswith(DEPENDS_MARKER):

                l = line[len(DEPENDS_MARKER):]
                l = l.strip()

                # Split on both space and comma.
                l = re.split(r'[ ,]+', l)

                depends.extend(l)

    return depends


def path_extract(path):
    """Extracts a declared build path from a given formula."""

    with open(path) as f:
        for line in f:
            # Build Path: /app/.heroku/usr/local
            if line.startswith(BUILD_PATH_MARKER):

                l = line[len(BUILD_PATH_MARKER):]
                l = l.strip()

                return l


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError:
        pass


def process(cmd, cwd=None):
    """A simple wrapper around the subprocess module."""
    p = Popen(cmd, cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
    return p


def pipe(a, b, indent=True):
    """Pipes stream A to stream B, with optional indentation."""
    for line in a:

        if indent:
            b.write('    ')

        b.write(line)


def targz_tree(dir, output):
    """Creates a tar.gz archive from a given directory."""
    with tarfile.open(output, 'w:gz') as tar:
        tar.add(dir, arcname=os.path.basename(dir))
