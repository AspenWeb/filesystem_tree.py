import os
from os.path import isdir

import pytest
from filesystem_tree import FilesystemTree


@pytest.yield_fixture
def fs():
    fs = FilesystemTree()
    yield fs
    fs.remove()


def test_it_can_be_instantiated():
    assert FilesystemTree().__class__.__name__ == 'FilesystemTree'

def test_args_go_to_mk_not_root():
    fs = FilesystemTree('foo', 'bar')
    assert fs.root != 'foo'

def test_it_makes_a_directory(fs):
    assert isdir(fs.root)

def test_resolve_resolves(fs):
    path = fs.resolve('some/dir')
    assert path == os.path.realpath(os.sep.join([fs.root, 'some', 'dir']))

def test_mk_makes_a_dir(fs):
    fs.mk('some/dir')
    assert isdir(fs.resolve('some/dir'))

def test_remove_removes(fs):
    assert isdir(fs.root)
    fs.remove()
    assert not isdir(fs.root)
