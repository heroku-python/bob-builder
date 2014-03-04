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
