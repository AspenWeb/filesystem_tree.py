#!/bin/sh -e
python filesystem_tree.py
py.test -v tests.py 
