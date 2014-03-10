# -*- coding: utf-8 -*-

import os
import envoy
import sys

from .utils import depends_extract, build_path_extract, mkdir_p, shell, indent

WORKSPACE = 'workspace'
DEFAULT_BUILD_PATH = '/app/.heroku/'
HOME_PWD = os.getcwd()

class Formula(object):

    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return '<Formula {}>'.format(self.path)

    @property
    def workspace_path(self):
        return os.path.join(WORKSPACE, self.path)

    @property
    def full_path(self):
        return os.path.abspath(self.workspace_path)

    @property
    def exists(self):
        """Returns True if the forumla appears to exist."""
        return os.path.exists(self.workspace_path)

    @property
    def depends_on(self):
        # TODO: full cascade? (e.g. resolve first?)
        return depends_extract(self.full_path)

    @property
    def build_path(self):
        return build_path_extract(self.full_path) or DEFAULT_BUILD_PATH

    def build(self):

        print self.build_path

        # Prepare build directory.
        mkdir_p(self.build_path)
        # os.chdir(self.build_path)

        # Execute the formula script.
        cmd = [self.full_path, self.build_path]

        p = shell(cmd, cwd=self.build_path)

        # Pipe the output to stdout.
        for line in p.stdout:
            sys.stdout.write(indent(line))

        # p.wait()

        # print p







