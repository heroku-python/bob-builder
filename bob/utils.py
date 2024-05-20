# -*- coding: utf-8 -*-

from __future__ import print_function

import errno
import os
import sys
import tarfile

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from fnmatch import fnmatchcase
from natsort import natsorted

from collections import namedtuple

Bucket = namedtuple('Bucket', ['bucket', 'anon'], defaults=[False])

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
# e.g. get_with_wildcard("foobar/dep-1.2.3.tar.gz") fetches that version
# e.g. get_with_wildcard("foobar/dep-1.2.*.tar.gz") fetches the "latest" matching
def get_with_wildcard(bucket, name):
    parts = name.partition("*")
    
    if not parts[1]: # no "*" in name
        ret = bucket.Object(name)
        try:
            ret.load()
            return ret
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return None
            raise
    
    firstparts = bucket.objects.filter(Prefix=parts[0]) # use anything before "*" as the prefix for S3 listing
    matches = [i for i in firstparts if fnmatchcase(i.key, name)] # fnmatch entire name with wildcard against found keys in S3 - prefix for "dep-1.2.*.tar.gz" was "dep-1.2", but there might be a "dep-1.2.3.sig" or whatnot
    # natsorted will sort correctly by version parts, even if the element is something like "dep-1.2.3.tar.gz"
    try:
        return natsorted(matches, key=lambda dep: dep.key).pop().Object()
    except IndexError:
        # list was empty
        return None

class S3ConnectionHandler(object):
    """
    A wrapper around boto's connect_s3() that automates fall-back to anonymous mode.

    This allows for unauthenticated retrieval from public buckets when the credentials
    boto finds in the environment don't permit access to the bucket, or when boto was
    unable to find any credentials at all.

    Returns a named tuple containing a boto3 Bucket resource object and an anonymous mode indicator.
    """

    buckets = {}
    all_anon = True

    def __init__(self):
        sts = boto3.client('sts')
        try:
            sts.get_caller_identity()
            self.all_anon = False
        except NoCredentialsError:
            print_stderr('No AWS credentials found. Requests will be made without authentication.',
                         title='WARNING')

    def get_bucket(self, name, region_name=None, force_anon=False):
        if name in self.buckets:
            return self.buckets[name]

        if self.all_anon:
            force_anon = True

        config = Config(region_name=region_name, s3={'us_east_1_regional_endpoint': 'regional'})
        if force_anon:
            config.signature_version = UNSIGNED

        s3 = boto3.resource('s3', config=config)

        try:
            # see if the bucket exists
            s3.meta.client.head_bucket(Bucket=name)
        except ClientError as e:
            if e.response['Error']['Code'] == "403":
                # we got a 403 on the HEAD request, but that doesn't mean we don't have access at all
                # just that we cannot perform a HEAD
                # if we're currently authenticated, then we fall back to anonymous, since we'll just want to try GETs on objects and bucket listings
                # otherwise, we'll just have to bubble through to the end, and see what happens on subsequent GETs
                if not force_anon:
                    print_stderr('Access denied for bucket "{}" using found credentials. '
                                 'Retrying as an anonymous user.'.format(name), title='NOTICE')
                    return self.get_bucket(name, region_name=region_name, force_anon=True)
            else:
                raise

        self.buckets[name] = Bucket(s3.Bucket(name), anon=force_anon)
        return self.buckets[name]
