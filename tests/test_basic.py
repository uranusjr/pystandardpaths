#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_standardpaths
----------------------------------

Tests for `standardpaths` module.
"""

import os
import pathlib
import platform
import sys
import unittest

from nose.plugins.skip import SkipTest
from nose.tools import nottest, eq_, assert_is_instance
from PyQt5.QtCore import qVersion, QCoreApplication, QStandardPaths

from standardpaths import (
    Location, configure, get_writable_path, get_standard_paths,
)


qt_version = tuple(int(c) for c in qVersion().split('.'))


def test_get_writable_path_string():
    eq_(get_writable_path('desktop'), get_writable_path(Location.desktop))


def nottest_unless(criteria):

    def _nottest_unless(f):
        if criteria:
            return f
        return nottest(f)

    return _nottest_unless


def nottest_if(criteria):

    def _nottest_if(f):
        if not criteria:
            return f
        return nottest(f)

    return _nottest_if


class EnumValuesMixin(object):

    @classmethod
    def setup_class(cls):
        cls.enum_values = set([v for v in Location])
        cls.app = QCoreApplication(sys.argv)
        cls.app.setApplicationName('Yksom')
        cls.app.setOrganizationName('uranusjr')
        configure(application_name='Yksom', organization_name='uranusjr')

    @classmethod
    def teardown_class(cls):
        # Make sure all locations are tested.
        eq_(cls.enum_values, set())

    def setUp(self):
        value_name = self._testMethodName.split('__')[-1]
        if value_name != 'data':    # "data" is covered by "app_local_data"
            self.enum_values.remove(Location[value_name])


class GetWritablePathTests(EnumValuesMixin, unittest.TestCase):

    def _test_against_qt(self, location, qt_location):
        path = get_writable_path(location)
        assert_is_instance(path, pathlib.Path)
        eq_(path.as_posix(), QStandardPaths.writableLocation(qt_location))

    def test__desktop(self):
        self._test_against_qt(Location.desktop, QStandardPaths.DesktopLocation)

    def test__documents(self):
        self._test_against_qt(
            Location.documents, QStandardPaths.DocumentsLocation,
        )

    def test__fonts(self):
        self._test_against_qt(Location.fonts, QStandardPaths.FontsLocation)

    def test__applications(self):
        self._test_against_qt(
            Location.applications, QStandardPaths.ApplicationsLocation,
        )

    def test__music(self):
        self._test_against_qt(Location.music, QStandardPaths.MusicLocation)

    def test__movies(self):
        self._test_against_qt(Location.movies, QStandardPaths.MoviesLocation)

    def test__pictures(self):
        self._test_against_qt(
            Location.pictures, QStandardPaths.PicturesLocation,
        )

    def test__temp(self):
        self._test_against_qt(Location.temp, QStandardPaths.TempLocation)

    def test__home(self):
        self._test_against_qt(Location.home, QStandardPaths.HomeLocation)

    def test__data(self):
        self._test_against_qt(Location.data, QStandardPaths.DataLocation)

    def test__cache(self):
        self._test_against_qt(Location.cache, QStandardPaths.CacheLocation)

    def test__generic_data(self):
        self._test_against_qt(
            Location.generic_data, QStandardPaths.GenericDataLocation,
        )

    def test__runtime(self):
        self._test_against_qt(Location.runtime, QStandardPaths.RuntimeLocation)

    def test__config(self):
        self._test_against_qt(Location.config, QStandardPaths.ConfigLocation)

    def test__download(self):
        self._test_against_qt(
            Location.download, QStandardPaths.DownloadLocation,
        )

    def test__generic_cache(self):
        self._test_against_qt(
            Location.generic_cache, QStandardPaths.GenericCacheLocation,
        )

    def test__generic_config(self):
        self._test_against_qt(
            Location.generic_config, QStandardPaths.GenericConfigLocation,
        )

    def test__app_data(self):
        if qt_version < (5, 4, 1):
            raise SkipTest
        self._test_against_qt(
            Location.app_data, QStandardPaths.AppDataLocation,
        )

    def test__app_local_data(self):
        if qt_version < (5, 4, 1):
            raise SkipTest
        self._test_against_qt(
            Location.app_local_data, QStandardPaths.AppLocalDataLocation,
        )

    @nottest_unless(platform.system() == 'Darwin')
    def test_osx__log(self):
        eq_(get_writable_path(Location.log),
            pathlib.Path(os.path.expanduser('~/Library/Logs/uranusjr/Yksom')))

    @nottest_unless(platform.system() == 'Windows')
    def test_windows__log(self):
        eq_(get_writable_path(Location.log),
            get_writable_path(Location.app_local_data) / 'log')

    @nottest_if(platform.system() in ('Darwin', 'Windows',))
    def test_unix__log(self):
        eq_(get_writable_path(Location.log),
            get_writable_path(Location.cache) / 'log')


class GetStandardPathsTests(EnumValuesMixin, unittest.TestCase):

    def _test_against_qt(self, location, qt_location):
        paths = get_standard_paths(location)
        path_strs = []
        for path in paths:
            assert_is_instance(path, pathlib.Path)
            path_strs.append(path.as_posix())
        eq_(path_strs, QStandardPaths.standardLocations(qt_location))

    def test__desktop(self):
        self._test_against_qt(Location.desktop, QStandardPaths.DesktopLocation)

    def test__documents(self):
        self._test_against_qt(
            Location.documents, QStandardPaths.DocumentsLocation,
        )

    def test__fonts(self):
        self._test_against_qt(Location.fonts, QStandardPaths.FontsLocation)

    def test__applications(self):
        self._test_against_qt(
            Location.applications, QStandardPaths.ApplicationsLocation,
        )

    def test__music(self):
        self._test_against_qt(Location.music, QStandardPaths.MusicLocation)

    def test__movies(self):
        self._test_against_qt(Location.movies, QStandardPaths.MoviesLocation)

    def test__pictures(self):
        self._test_against_qt(
            Location.pictures, QStandardPaths.PicturesLocation,
        )

    def test__temp(self):
        self._test_against_qt(Location.temp, QStandardPaths.TempLocation)

    def test__home(self):
        self._test_against_qt(Location.home, QStandardPaths.HomeLocation)

    def test__data(self):
        paths = get_standard_paths(Location.data)
        path_strs = []
        for path in paths:
            assert_is_instance(path, pathlib.Path)
            path_strs.append(path.as_posix())
        qt_path_strs = QStandardPaths.standardLocations(
            QStandardPaths.DataLocation,
        )
        if platform.system() == 'Darwin':
            # Exclude bundle path on OS X. See comments in
            # `get_standard_paths` implementation for more information.
            if qt_path_strs[-1].rstrip('/').endswith('Python.app'):
                qt_path_strs = qt_path_strs[:-1]
        elif platform.system() == 'Windows':
            # Exclude paths relative to executable. See comments in
            # `get_standard_paths` implementation for more information.
            python_loc = (pathlib.Path(sys.executable) / '..').resolve()
            qt_path_strs = [
                ps for ps in qt_path_strs
                if ps not in (
                    python_loc.as_posix(), (python_loc / 'data').as_posix(),
                )
            ]
        eq_(path_strs, qt_path_strs)

    def test__cache(self):
        self._test_against_qt(Location.cache, QStandardPaths.CacheLocation)

    def test__generic_data(self):
        self._test_against_qt(
            Location.generic_data, QStandardPaths.GenericDataLocation,
        )

    def test__runtime(self):
        self._test_against_qt(Location.runtime, QStandardPaths.RuntimeLocation)

    def test__config(self):
        paths = get_standard_paths(Location.config)
        path_strs = []
        for path in paths:
            assert_is_instance(path, pathlib.Path)
            path_strs.append(path.as_posix())
        qt_path_strs = QStandardPaths.standardLocations(
            QStandardPaths.ConfigLocation,
        )
        if platform.system() == 'Windows':
            # Exclude paths relative to executable. See comments in
            # `get_standard_paths` implementation for more information.
            python_loc = (pathlib.Path(sys.executable) / '..').resolve()
            qt_path_strs = [
                ps for ps in qt_path_strs
                if ps not in (
                    python_loc.as_posix(), (python_loc / 'data').as_posix(),
                )
            ]
        eq_(path_strs, qt_path_strs)

    def test__download(self):
        self._test_against_qt(
            Location.download, QStandardPaths.DownloadLocation,
        )

    def test__generic_cache(self):
        self._test_against_qt(
            Location.generic_cache, QStandardPaths.GenericCacheLocation,
        )

    def test__generic_config(self):
        paths = get_standard_paths(Location.generic_config)
        path_strs = []
        for path in paths:
            assert_is_instance(path, pathlib.Path)
            path_strs.append(path.as_posix())
        qt_path_strs = QStandardPaths.standardLocations(
            QStandardPaths.GenericConfigLocation,
        )
        if platform.system() == 'Windows':
            # Exclude paths relative to executable. See comments in
            # `get_standard_paths` implementation for more information.
            python_loc = (pathlib.Path(sys.executable) / '..').resolve()
            qt_path_strs = [
                ps for ps in qt_path_strs
                if ps not in (
                    python_loc.as_posix(), (python_loc / 'data').as_posix(),
                )
            ]
        eq_(path_strs, qt_path_strs)

    def test__app_data(self):
        if qt_version < (5, 4, 1):
            raise SkipTest
        paths = get_standard_paths(Location.app_data)
        path_strs = []
        for path in paths:
            assert_is_instance(path, pathlib.Path)
            path_strs.append(path.as_posix())
        qt_path_strs = QStandardPaths.standardLocations(
            QStandardPaths.AppDataLocation,
        )
        if platform.system() == 'Darwin':
            # Exclude bundle path on OS X. See comments in
            # `get_standard_paths` implementation for more information.
            if qt_path_strs[-1].rstrip('/').endswith('Python.app'):
                qt_path_strs = qt_path_strs[:-1]
        elif platform.system() == 'Windows':
            # Exclude paths relative to executable. See comments in
            # `get_standard_paths` implementation for more information.
            python_loc = (pathlib.Path(sys.executable) / '..').resolve()
            qt_path_strs = [
                ps for ps in qt_path_strs
                if ps not in (
                    python_loc.as_posix(), (python_loc / 'data').as_posix(),
                )
            ]
        eq_(path_strs, qt_path_strs)

    def test__app_local_data(self):
        if qt_version < (5, 4, 1):
            raise SkipTest
        paths = get_standard_paths(Location.app_local_data)
        path_strs = []
        for path in paths:
            assert_is_instance(path, pathlib.Path)
            path_strs.append(path.as_posix())
        qt_path_strs = QStandardPaths.standardLocations(
            QStandardPaths.AppLocalDataLocation,
        )
        if platform.system() == 'Darwin':
            # Exclude bundle path on OS X. See comments in
            # `get_standard_paths` implementation for more information.
            if qt_path_strs[-1].rstrip('/').endswith('Python.app'):
                qt_path_strs = qt_path_strs[:-1]
        elif platform.system() == 'Windows':
            # Exclude paths relative to executable. See comments in
            # `get_standard_paths` implementation for more information.
            python_loc = (pathlib.Path(sys.executable) / '..').resolve()
            qt_path_strs = [
                ps for ps in qt_path_strs
                if ps not in (
                    python_loc.as_posix(), (python_loc / 'data').as_posix(),
                )
            ]
        eq_(path_strs, qt_path_strs)

    @nottest_unless(platform.system() == 'Darwin')
    def test_osx__log(self):
        exp = pathlib.Path(os.path.expanduser('~/Library/Logs/uranusjr/Yksom'))
        eq_(get_standard_paths(Location.log), [exp])

    @nottest_unless(platform.system() == 'Windows')
    def test_windows__log(self):
        eq_(get_standard_paths(Location.log),
            [get_writable_path(Location.app_local_data) / 'log'])

    @nottest_if(platform.system() in ('Darwin', 'Windows',))
    def test_unix__log(self):
        eq_(get_standard_paths(Location.log),
            [get_writable_path(Location.cache) / 'log'])
