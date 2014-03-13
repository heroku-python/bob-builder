# -*- coding: utf-8 -*-

import os
import envoy
import sys
from tempfile import mkstemp

import re

import boto
from boto.s3.key import Key

from .utils import *

WORKSPACE = os.environ.get('WORKSPACE', 'workspace')
DEFAULT_BUILD_PATH = os.environ.get('DEFAULT_BUILD_PATH', '/app/.heroku/')
AWS_BUCKET = os.environ.get('AWS_BUCKET')
HOME_PWD = os.getcwd()

DEPS_MARKER = '# Build Deps: '
BUILD_PATH_MARKER = '# Build Path: '

s3 = boto.connect_s3()
bucket = s3.get_bucket(AWS_BUCKET)

# Make stdin/out as unbuffered as possible via file descriptor modes.
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)


class Formula(object):

    def __init__(self, path):
        self.path = path
        self.archived_path = None

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
        """Extracts a list of declared dependencies from a given formula."""
        # Depends: libraries/libsqlite, libraries/libsqlite

        depends = []

        for result in iter_marker_lines(DEPS_MARKER, self.full_path):
            # Split on both space and comma.
            result = re.split(r'[ ,]+', result)
            depends.extend(result)

            return depends


    @property
    def build_path(self):
        """Extracts a declared build path from a given formula."""

        for result in iter_marker_lines(BUILD_PATH_MARKER, self.full_path):
            return result

        # If none was provided, fallback to default.
        return DEFAULT_BUILD_PATH


    def resolve_deps(self):

        # Dependency metadata, extracted from bash comments.
        deps = self.depends_on
        print

        if deps:
            print 'Fetching dependencies... found {}:'.format(len(deps))

            for dep in deps:
                print '  - {}'.format(dep)

                key_name = '{}.tar.gz'.format(dep)
                key = bucket.get_key(key_name)

                if not key:
                    print
                    print 'WARNING: Archive {} does not exist.'.format(key_name)
                    print '    Please deploy it to continue.'
                    exit()

                # Grab the Dep from S3, download it to a temp file.
                archive = mkstemp()[1]
                key.get_contents_to_filename(archive)

                # Extract the Dep to the appropriate location.
                extract_tree(archive, self.build_path)

    def build(self):
        # Prepare build directory.
        mkdir_p(self.build_path)

        self.resolve_deps()

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
        """Archives the build directory as a tar.gz."""
        archive = mkstemp()[1]
        archive_tree(self.build_path, archive)

        print archive
        self.archived_path = archive


    def deploy(self, allow_overwrite=False):
        """Deploys the formula's archive to S3."""
        assert self.archived_path

        key_name = '{}.tar.gz'.format(self.path)
        key = bucket.get_key(key_name)

        if key:
            if not allow_overwrite:
                print 'WARNING: Archive {} already exists.'.format(key_name)
                print '    Use the --overwrite flag to continue.'
                exit()
        else:
            key = bucket.new_key(key_name)

        # Upload the archive, set permissions.
        key.set_contents_from_filename(self.archived_path)
        key.set_acl('public-read')




