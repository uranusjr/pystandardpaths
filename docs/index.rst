===============
PyStandardPaths
===============

PyStandardPaths provides methods for accessing standard paths.

This module contains functions to query standard locations on the local filesystem, for common tasks such as user-specific directories or system-wide configuration directories. The functions, location names, and the implementation of how paths are calculated, are based on Qt 5's `QStandardPaths`_ class.

The current implementation matches that of Qt 5.4.1. This matching-Qt-version information can be obtained via :const:`standardpaths.QTVERSION` (as a tuple of integers) and :const:`standardpaths.__qtversion__` (as a string).


Installation
============

PyStandardPaths can be installed with `pip`::

    pip install pystandardpaths

Currently OS X, Windows, and Unix systems conforming to `freedesktop.org`_ specifications are supported.

Implementations on OS X and Windows are based on :mod:`ctypes`, and dependencies vary between operating systems and Python versions.


Contents
========

.. toctree::
   :maxdepth: 2

   usage
   references
   contributing
   authors
   history


.. _`QStandardPaths`: http://doc.qt.io/qt-5/qstandardpaths.html
.. _`freedesktop.org`: http://www.freedesktop.org
