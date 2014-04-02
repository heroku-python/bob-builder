# -*- coding: utf-8 -*-

import os
import re
import tarfile
from subprocess import Popen, PIPE

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
    except OSError:
        pass


def process(cmd, cwd=None):
    """A simple wrapper around the subprocess module."""
    p = Popen(cmd, cwd=cwd, shell=False, stdout=PIPE, stderr=PIPE)
    return p


def pipe(a, b, indent=True):
    """Pipes stream A to stream B, with optional indentation."""

    for line in a:

        if indent:
            b.write('    ')

        b.write(line)


def archive_tree(dir, archive):
    """Creates a tar.gz archive from a given directory."""

    abspath = os.path.abspath(dir)
    base_root = None
    is_top_level = False

    with tarfile.open(archive, 'w:gz') as tar:

        for root, _, files in os.walk(abspath):

            # Mark the first pass as the top-level directory.
            if is_top_level is None:
                is_top_level = True

            if not base_root:
                base_root = root

            transposed_base = root[len(base_root)+1:]

            for file in files:

                standard_path = os.path.join(root, file)

                if is_top_level:
                    transposed_path = file
                else:
                    transposed_path = os.path.join(transposed_base, file)

                # Add the file to the archive, with the proper transposed path.
                tar.add(standard_path, arcname=transposed_path)

            # Close out the top-level directory marker.
            is_top_level = False


def extract_tree(archive, dir):
    """Extract tar.gz archive to a given directory."""
    with tarfile.open(archive, 'r:gz') as tar:
        tar.extractall(dir)
