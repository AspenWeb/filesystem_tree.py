#!/bin/sh
python filesystem_fixture.py -v
py.test -v tests.py 
