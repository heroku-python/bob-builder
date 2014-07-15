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

 * Create a Heroku app and push the build toolkit to it.
   (`$ heroku create build-toolkit-python-staging --buildpack https://github.com/kennethreitz/conda-buildpack.git`)
 * Add your S3 credentials to the application
   (`AWS_ACCESS_KEY_ID`,`AWS_SECRET_ACCESS_KEY`, and `S3_BUCKET`)
 * `local$ heroku run bash`
 * `dyno$ bob build runtimes/python-2.7.6`
 * `dyno$ bob deploy runtimes/python-2.7.6`


