# Binary Build Toolkit

This repo exists as a framework for the compilation and deployment of binaries and libraries on Heroku.

It is inspired by (and extracted from) [kennethreitz/python-versions](https://github.com/kennethreitz/python-versions).

## Intended Design

- Flexible type hierarchy
- Flat dependency resolution
- Version agnostic (careful curation and naming conventions preferred)
- Import already-deployed sub-dependencies during a build

## Powered By

- Bash, mostly
- A litle bit of Python
- Boto

## Getting Started (Staging)

 * `$ heroku create build-toolkit-python-staging --buildpack https://github.com/kennethreitz/conda-buildpack.git`
 * `$ heroku config:set AWS_ACCESS_KEY_ID=xxx AWS_SECRET_ACCESS_KEY=xxx S3_BUCKET=xxx`
 
```
$ heroku run bash
  $ bob build runtimes/python-2.7.6
  $ bob deploy runtimes/python-2.7.6


