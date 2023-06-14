#!/bin/bash

# Clean up old distribution, build directories, and egg-info
rm -rf dist/
rm -rf build/
rm -rf pythonnative.egg-info/

# Generate distribution archives
python setup.py sdist bdist_wheel

# Upload the distribution archives to PyPi
twine upload dist/*
