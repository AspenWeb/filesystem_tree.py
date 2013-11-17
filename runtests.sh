#!/bin/sh
python filesystem_fixture.py
py.test -v tests.py 
