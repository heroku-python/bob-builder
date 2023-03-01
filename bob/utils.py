# -*- coding: utf-8 -*-

from __future__ import print_function

import errno
import os
import sys
import tarfile

import boto
from boto.exception import NoAuthHandlerFound, S3ResponseError

from distutils.version import LooseVersion
from fnmatch import fnmatchcase

def print_stderr(message='', title=''):
    print(('\n{1}: {0}\n' if title else '{0}').format(message, title), file=sys.stderr)


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


def archive_tree(dir, archive):
    """Creates a tar.gz archive from a given directory."""
    with tarfile.open(archive, 'w:gz') as tar:
        # do not tar.add(dir) with empty arcname, that will create a "/" entry and tar will complain when extracting
        for item in os.listdir(dir):
            tar.add(dir+"/"+item, arcname=item)


def extract_tree(archive, dir):
    """Extract tar.gz archive to a given directory."""
    with tarfile.open(archive, 'r:gz') as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, dir)

# get a key, or the highest matching (as in software version) key if it contains wildcards
# e.g. get_with_wildcard("foobar/dep-1.2.3") fetches that version
# e.g. get_with_wildcard("foobar/dep-1.2.*") fetches the "latest" matching
def get_with_wildcard(bucket, name):
    parts = name.partition("*")
    
    if not parts[1]: # no "*" in name
        return bucket.get_key(name)
    
    firstparts = bucket.list(parts[0]) # use anything before "*" as the prefix for S3 listing
    matches = [i for i in firstparts if fnmatchcase(i.name, name)] # fnmatch against found keys in S3
    
    matches.sort(key=lambda dep: LooseVersion(dep.name), reverse=True)
    
    return next(iter(matches), None) # return first item or None

class S3ConnectionHandler(object):
    """
    A wrapper around boto's connect_s3() that automates fall-back to anonymous mode.

    This allows for unauthenticated retrieval from public buckets when the credentials
    boto finds in the environment don't permit access to the bucket, or when boto was
    unable to find any credentials at all.

    Returns a boto S3Connection object.
    """

    def __init__(self):
        try:
            self.s3 = boto.connect_s3()
        except NoAuthHandlerFound:
            print_stderr('No AWS credentials found. Requests will be made without authentication.',
                         title='WARNING')
            self.s3 = boto.connect_s3(anon=True)

    def get_bucket(self, name):
        try:
            return self.s3.get_bucket(name)
        except S3ResponseError as e:
            if e.status == 403 and not self.s3.anon:
                print_stderr('Access denied for bucket "{}" using found credentials. '
                             'Retrying as an anonymous user.'.format(name), title='NOTICE')
                if not hasattr(self, 's3_anon'):
                    self.s3_anon = boto.connect_s3(anon=True)
                return self.s3_anon.get_bucket(name)
            raise
