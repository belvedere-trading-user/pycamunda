#!/bin/bash -xe
pylint pycamunda
python setup.py coverage
doxygen 2> doxygen.err
vigilance
