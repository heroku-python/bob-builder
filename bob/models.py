# -*- coding: utf-8 -*-

import os
import envoy
import shutil
import sys
from tempfile import mkstemp, mkdtemp

import re

import boto
from boto.s3.key import Key

from .utils import *

WORKSPACE = os.environ.get('WORKSPACE_DIR', 'workspace')
DEFAULT_BUILD_PATH = os.environ.get('DEFAULT_BUILD_PATH', '/app/.heroku/')
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_PREFIX = os.environ.get('S3_PREFIX', '')
UPSTREAM_S3_BUCKET = os.environ.get('UPSTREAM_S3_BUCKET')
UPSTREAM_S3_PREFIX = os.environ.get('UPSTREAM_S3_PREFIX', '')

# Append a slash for backwards compatibility.
if S3_PREFIX and not S3_PREFIX.endswith('/'):
    S3_PREFIX = '{0}/'.format(S3_PREFIX)
if UPSTREAM_S3_PREFIX and not UPSTREAM_S3_PREFIX.endswith('/'):
    UPSTREAM_S3_PREFIX = '{0}/'.format(UPSTREAM_S3_PREFIX)

DEPS_MARKER = '# Build Deps: '
BUILD_PATH_MARKER = '# Build Path: '

s3 = boto.connect_s3()
bucket = s3.get_bucket(S3_BUCKET)
upstream = None
if UPSTREAM_S3_BUCKET:
    upstream = s3.get_bucket(UPSTREAM_S3_BUCKET)

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

                key_name = '{}{}.tar.gz'.format(S3_PREFIX, dep)
                key = bucket.get_key(key_name)

                if not key and upstream:
                    print '    Not found in S3_BUCKET, trying UPSTREAM_S3_BUCKET...'
                    key_name = '{}{}.tar.gz'.format(UPSTREAM_S3_PREFIX, dep)
                    key = upstream.get_key(key_name)

                if not key:
                    print
                    print 'ERROR: Archive {} does not exist.'.format(key_name)
                    print '    Please deploy it to continue.'
                    sys.exit(1)

                # Grab the Dep from S3, download it to a temp file.
                archive = mkstemp()[1]
                key.get_contents_to_filename(archive)

                # Extract the Dep to the appropriate location.
                extract_tree(archive, self.build_path)

    def build(self):
        # Prepare build directory.
        if os.path.exists(self.build_path):
                shutil.rmtree(self.build_path)
        mkdir_p(self.build_path)

        self.resolve_deps()

        # Temporary directory where work will be carried out, because of David.
        cwd_path = mkdtemp(prefix='bob')

        print 'Building formula {} in {}:'.format(self.path, cwd_path)

        # Execute the formula script.
        cmd = [self.full_path, self.build_path]
        p = process(cmd, cwd=cwd_path)

        pipe(p.stdout, sys.stdout, indent=True)
        p.wait()

        if p.returncode != 0:
            print
            print 'ERROR: An error occurred.'
            sys.exit(1)


    def archive(self):
        """Archives the build directory as a tar.gz."""
        archive = mkstemp()[1]
        archive_tree(self.build_path, archive)

        print archive
        self.archived_path = archive


    def deploy(self, allow_overwrite=False):
        """Deploys the formula's archive to S3."""
        assert self.archived_path

        key_name = '{}{}.tar.gz'.format(S3_PREFIX, self.path)
        key = bucket.get_key(key_name)

        if key:
            if not allow_overwrite:
                print 'ERROR: Archive {} already exists.'.format(key_name)
                print '    Use the --overwrite flag to continue.'
                sys.exit(1)
        else:
            key = bucket.new_key(key_name)

        # Upload the archive, set permissions.
        key.set_contents_from_filename(self.archived_path)
        key.set_acl('public-read')
