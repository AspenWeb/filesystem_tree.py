from __future__ import absolute_import, division, print_function, unicode_literals

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

def test_mk_makes_a_dir_is_like_dash_p(fs):
    fs.mk('some/dir', 'some/dir')
    assert isdir(fs.resolve('some/dir'))

def test_mk_makes_a_file(fs):
    fs.mk(('some/dir/file.txt', 'Greetings, program!'))
    contents = open(fs.resolve('some/dir/file.txt')).read()
    assert contents == 'Greetings, program!'

def test_mk_makes_a_file_with_unicode_content(fs):
    fs.mk(('some/dir/file.txt', '\u2603'))
    contents = open(fs.resolve('some/dir/file.txt')).read()
    assert contents == 'Greetings, program!'

def test_mk_doesnt_choke_on_existing_dir(fs):
    fs.mk('some/dir', ('some/dir/file.txt', 'Greetings, program!'))
    contents = open(fs.resolve('some/dir/file.txt')).read()
    assert contents == 'Greetings, program!'

def test_remove_removes(fs):
    assert isdir(fs.root)
    fs.remove()
    assert not isdir(fs.root)

def test_resolve_with_no_arg_is_equivalent_to_root(fs):
    assert fs.resolve() == fs.root


# should_dedent - sd

def test_sd_defaults_to_true(fs):
    fs.mk(('some/dir/file.txt', '    Greetings, program!'))
    contents = open(fs.resolve('some/dir/file.txt')).read()
    assert contents == 'Greetings, program!'

def test_sd_false_via_tuple(fs):
    fs.mk(('some/dir/file.txt', '    Greetings, program!', 0), should_dedent=1)
    contents = open(fs.resolve('some/dir/file.txt')).read()
    assert contents == '    Greetings, program!'

def test_sd_true_via_tuple(fs):
    fs.mk(('some/dir/file.txt', '    Greetings, program!', 1), should_dedent=0)
    contents = open(fs.resolve('some/dir/file.txt')).read()
    assert contents == 'Greetings, program!'

def test_sd_false_via_mk(fs):
    fs.mk(('some/dir/file.txt', '    Greetings, program!'), should_dedent=False)
    contents = open(fs.resolve('some/dir/file.txt')).read()
    assert contents == '    Greetings, program!'

def test_sd_true_via_mk(fs):
    fs.mk(('some/dir/file.txt', '    Greetings, program!'), should_dedent=1)
    contents = open(fs.resolve('some/dir/file.txt')).read()
    assert contents == 'Greetings, program!'

def test_sd_false_via_constructor():
    try:
        fs = FilesystemTree(should_dedent=False)
        fs.mk(('some/dir/file.txt', '    Greetings, program!'))
        contents = open(fs.resolve('some/dir/file.txt')).read()
        assert contents == '    Greetings, program!'
    finally:
        fs.remove()

def test_sd_true_via_constructor():
    try:
        FilesystemTree.should_dedent = False
        fs = FilesystemTree(should_dedent=True)
        fs.mk(('some/dir/file.txt', '    Greetings, program!'))
        contents = open(fs.resolve('some/dir/file.txt')).read()
        assert contents == 'Greetings, program!'
    finally:
        FilesystemTree.should_dedent = True
        fs.remove()

def test_sd_false_via_instance_attribute():
    try:
        fs = FilesystemTree()
        fs.should_dedent = False
        fs.mk(('some/dir/file.txt', '    Greetings, program!'))
        contents = open(fs.resolve('some/dir/file.txt')).read()
        assert contents == '    Greetings, program!'
    finally:
        fs.remove()

def test_sd_true_via_instance_attribute():
    try:
        fs = FilesystemTree(should_dedent=False)
        fs.should_dedent = True
        fs.mk(('some/dir/file.txt', '    Greetings, program!'))
        contents = open(fs.resolve('some/dir/file.txt')).read()
        assert contents == 'Greetings, program!'
    finally:
        fs.remove()

def test_sd_false_via_class_attribute():
    try:
        FilesystemTree.should_dedent = False
        fs = FilesystemTree()
        fs.mk(('some/dir/file.txt', '    Greetings, program!'))
        contents = open(fs.resolve('some/dir/file.txt')).read()
        assert contents == 'Greetings, program!'
    finally:
        FilesystemTree.should_dedent = True
        fs.remove()
