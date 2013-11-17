"""This library provides a class for managing a filesystem tree. Test fixture
is the driving use-case.


Installation
------------

:py:mod:`filesystem_tree` is available on `GitHub`_ and on `PyPI`_::

    $ pip install filesystem_tree

We `test <https://travis-ci.org/gittip/filesystem_tree.py>`_ against
Python 2.6, 2.7, 3.2, and 3.3.

:py:mod:`filesystem_tree` is in the `public domain`_.


.. _GitHub: https://github.com/gittip/filesystem_tree.py
.. _PyPI: https://pypi.python.org/pypi/filesystem_tree
.. _public domain: http://creativecommons.org/publicdomain/zero/1.0/


API
---

"""
import os
import shutil
import sys
import tempfile
from textwrap import dedent

from os.path import dirname, isdir, realpath


__version__ = '1.0.0rc1'


if sys.version_info >= (3, 0, 0):
    is_stringy = lambda s: isinstance(s, str)
else:
    is_stringy = lambda s: isinstance(s, basestring)


class FilesystemTree(object):
    """Represent a filesystem tree.

    :param treedef: Any positional arguments are passed through to :py:func:`mk`.

    :param string root: The root of the filesystem tree. If not specified or
        ``None``, a temporary directory will be created and used. (May only be
        supplied as a keyword argument.)

    :param bool should_dedent: Sets the instance default for whether or not the
        contents of files are dedented before being written. (May only be supplied
        as a keyword argument.)

    Create a new instance of this class every time you need an isolated
    filesystem tree:

    >>> fs = FilesystemTree()

    This creates a temporary directory, the path to which you can access with
    ``fs.root``:

    >>> isdir(fs.root)
    True

    """

    prefix = 'filesystem-tree-' #: The prefix to use when making a temporary directory as root.
    root = None                 #: The root of the filesystem tree that this object represents.
    should_dedent = True        #: Whether or not to automatically dedent file contents on write.

    _sep = os.sep


    def __init__(self, *treedef, **kw):

        # Pull args out of kw.
        root = kw.get('root', None)
        should_dedent = kw.get('should_dedent', True)

        self.root = root if root is not None else realpath(tempfile.mkdtemp(prefix=self.prefix))
        self.should_dedent = should_dedent
        if treedef is not None:
            self.mk(*treedef)


    def mk(self, *treedef, **kw):
        """Builds a filesystem tree in :py:attr:`~FilesystemTree.root` based on ``treedef``.

        :param treedef:             The definition of a filesystem tree.

        :param bool should_dedent:  Controls whether or not the contents of
            files are dedented before being written. If not specified,
            :py:attr:`should_dedent` is used. (May only be supplied as a
            keyword argument.)

        :raises:                    :py:exc:`TypeError`, if treedef contains
            anything besides strings and tuples; :py:exc:`ValueError`, if
            treedef contains a tuple that doesn't have two or three items

        :returns: ``None``

        This method iterates over the items in ``treedef``, creating
        directories for any strings, and files for any tuples. For file tuples,
        the first item is the path of the file, the second is the contents to
        write, and the third (optional) item is whether to dedent the contents
        first before writing it. All paths must be specified using ``/`` as the
        separator (they will be automatically converted to the native path
        separator for the current platform). Any intermediate directories will
        be created as necessary.

        So for example if you instantiate a :py:class:`FilesystemTree`:

        >>> fs = FilesystemTree()

        And you call :py:func:`mk` with:

        >>> fs.mk(('path/to/file.txt', 'Greetings, program!'))

        Then you'll have one file in your tree:

        >>> os.listdir(os.path.join(fs.root, 'path', 'to'))
        ['file.txt']

        And it will have the content you asked for:

        >>> open(fs.resolve('path/to/file.txt')).read()
        'Greetings, program!'

        The automatic dedenting is so you can use multi-line strings in indented
        code blocks to specify file contents and indent it with the rest of your
        code, but not have the indents actually written to the file. For example:

        >>> def foo():
        ...     fs.mk(('other/file.txt', '''
        ...     Here is a list of things:
        ...         - Thing one.
        ...         - Thing two.
        ...         - Thing three.
        ...     '''))
        ...
        >>> foo()
        >>> print(open(fs.resolve('other/file.txt')).read())
        <BLANKLINE>
        Here is a list of things:
            - Thing one.
            - Thing two.
            - Thing three.
        <BLANKLINE>

        """
        should_dedent = kw.get('should_dedent', self.should_dedent)
        convert_path = lambda path: self._sep.join(path.split('/'))

        for item in treedef:
            if is_stringy(item):
                path = convert_path(item.lstrip('/'))
                path = self._sep.join([self.root, path])
                os.makedirs(path)
            elif isinstance(item, tuple):

                if len(item) == 2:
                    filepath, contents = item
                    should_dedent = should_dedent
                elif len(item) == 3:
                    filepath, contents, should_dedent = item
                else:
                    raise ValueError

                path = convert_path(filepath.lstrip('/'))
                path = self._sep.join([self.root, path])
                parent = dirname(path)
                os.makedirs(parent)

                if should_dedent:
                    contents = dedent(contents)

                open(path, 'w+').write(contents)

            else:
                raise TypeError


    def resolve(self, path=''):
        """Given a relative path, return an absolute path.

        :param path: A path relative to :py:attr:`root` using ``/`` as the separator

        :returns: An absolute path using the native path separator, with symlinks removed

        The return value of :py:func:`resolve` with no arguments is equivalent
        to :py:attr:`root`.

        """
        path = self._sep.join([self.root] + path.split('/'))
        return realpath(path)


    def remove(self):
        """Remove the filesystem tree at :py:attr:`root`.

        :returns: ``None``

        """
        if isdir(self.root):
            shutil.rmtree(self.root)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
