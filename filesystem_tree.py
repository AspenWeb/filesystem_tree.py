"""
API Reference
-------------
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shutil
import sys
import tempfile
from textwrap import dedent

from os.path import dirname, isdir, realpath


__version__ = '1.0.1-dev'


if sys.version_info >= (3, 0, 0):
    is_stringy = lambda s: isinstance(s, str)
    is_bytestring = lambda s: isinstance(s, bytes)
else:
    is_stringy = lambda s: isinstance(s, basestring)
    is_bytestring = lambda s: isinstance(s, str)


class FilesystemTree(object):
    """Represent a filesystem tree.

    :param treedef: Any positional arguments are passed through to :py:func:`mk`.

    :param string root: The root of the filesystem tree. If not specified or
        ``None``, a temporary directory will be created and used. (May only be
        supplied as a keyword argument.)

    :param bool should_dedent: Sets the instance default for whether or not the
        contents of files are dedented before being written. (May only be supplied
        as a keyword argument.)

    :param str encoding: Sets the instance default for what encoding to use when
        writing to disk. (May only be supplied as a keyword argument.)

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
    encoding = 'UTF-8'          #: How to encode file contents on write, when necessary.

    _sep = os.sep


    def __init__(self, *treedef, **kw):

        # Pull args out of kw.
        root = kw.get('root', self.root)
        should_dedent = kw.get('should_dedent', self.should_dedent)
        encoding = kw.get('encoding', self.encoding)

        self.root = root if root is not None else realpath(tempfile.mkdtemp(prefix=self.prefix))
        self.should_dedent = should_dedent
        self.encoding = encoding

        if treedef is not None:
            self.mk(*treedef)


    def __enter__(self):
        """support using a FilesystemTree as a context manager"""
        return self


    def __exit__(self, exc_type, exc_value, tb):
        """When exiting a context, only do cleanup if it was a clean exit"""
        if exc_type == None and exc_value == None and tb == None:
            self.remove()


    def mk(self, *treedef, **kw):
        """Builds a filesystem tree in :py:attr:`~FilesystemTree.root` based on ``treedef``.

        :param treedef:             The definition of a filesystem tree.

        :param bool should_dedent:  Controls whether or not the contents of
            files are dedented before being written. If not specified,
            :py:attr:`should_dedent` is used. (May only be supplied as a
            keyword argument.)

        :param str encoding:        The encoding with which to convert file
            contents to a bytestring if you specify said contents as a ``str``
            (Python 3) or ``unicode`` (Python 2). If not specified,
            :py:attr:`encoding` is used. (May only be supplied as a keyword
            argument.)

        :raises:                    :py:exc:`TypeError`, if treedef contains
            anything besides strings and tuples; :py:exc:`ValueError`, if
            treedef contains a tuple that doesn't have two or three items

        :returns: ``None``

        This method iterates over the items in ``treedef``, creating
        directories for any strings, and files for any tuples. For file tuples,
        the first item is the path of the file, the second is the contents to
        write, the third (optional) item is whether to dedent the contents
        first before writing it, and the fourth (optional) item is the encoding
        to use when writing the file. All paths must be specified using ``/``
        as the separator (they will be automatically converted to the native
        path separator for the current platform). Any intermediate directories
        will be created as necessary.

        So for example if you instantiate a :py:class:`FilesystemTree`:

        >>> fs = FilesystemTree()

        And you call :py:func:`mk` with:

        >>> fs.mk(('path/to/file.txt', 'Greetings, program!'))

        Then you'll have one file in your tree:

        >>> files = os.listdir(os.path.join(fs.root, 'path', 'to'))
        >>> print(' '.join(files))
        file.txt

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
        encoding = kw.get('encoding', self.encoding)
        convert_path = lambda path: self._sep.join(path.split('/'))

        for item in treedef:
            if is_stringy(item):
                path = convert_path(item.lstrip('/'))
                path = self._sep.join([self.root, path])
                if not isdir(path):
                    os.makedirs(path)
            elif isinstance(item, tuple):

                if len(item) == 2:
                    filepath, contents = item
                    should_dedent = should_dedent
                    encoding = encoding
                elif len(item) == 3:
                    filepath, contents, should_dedent = item
                    encoding = encoding
                elif len(item) == 4:
                    filepath, contents, should_dedent, encoding = item
                else:
                    raise ValueError

                path = convert_path(filepath.lstrip('/'))
                path = self._sep.join([self.root, path])
                parent = dirname(path)
                if not isdir(parent):
                    os.makedirs(parent)

                if should_dedent:
                    contents = dedent(contents)

                if not is_bytestring(contents):
                    contents = contents.encode(encoding)

                with open(path, 'wb+') as f:
                    f.write(contents)

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
    failures, tests = doctest.testmod()
    sys.exit(failures)

