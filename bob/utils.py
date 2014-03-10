# -*- coding: utf-8 -*-

import os
import re
from subprocess import Popen, PIPE


DEPENDS_MARKER = '# Build Deps: '
BUILD_PATH_MARKER = '# Build Path: '

def depends_extract(path):
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


def build_path_extract(path):
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

def shell(cmd, cwd=None):
    p = Popen(cmd, cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
    return p

def indent(s, n=4):
    template = (' ' * n) + '{}'
    template.format(s)
