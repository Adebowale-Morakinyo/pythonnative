#!/bin/bash

# Clean up old distribution and build directories
rm -rf dist/
rm -rf build/

# Generate distribution archives
python setup.py sdist bdist_wheel

# Upload the distribution archives to PyPi
twine upload dist/*
