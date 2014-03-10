# -*- coding: utf-8 -*-

import os
import envoy
import sys

from .utils import depends_extract, build_path_extract, mkdir_p, process, pipe

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

        # Prepare build directory.
        mkdir_p(self.build_path)

        print 'Building formula {}:'.format(self.path)

        # Execute the formula script.
        cmd = [self.full_path, self.build_path]
        p = process(cmd, cwd=self.build_path)

        pipe(p.stdout, sys.stdout, indent=True)
        p.wait()

        if p.returncode != 0:
            print
            print 'WARNING: An error occurred:'
            pipe(p.stderr, sys.stderr, indent=True)
            exit()


    def archive(self):
        pass

    def deploy(self):
        pass







