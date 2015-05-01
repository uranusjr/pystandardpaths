#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_standardpaths
----------------------------------

Tests for `standardpaths` module.
"""

import pathlib
import platform
import sys
import unittest

from PyQt5.QtCore import QCoreApplication, QStandardPaths

from standardpaths import (
    Location, configure, get_writable_path, get_standard_paths,
)


convert_table = {
    Location.desktop: QStandardPaths.DesktopLocation,
    Location.documents: QStandardPaths.DocumentsLocation,
    Location.fonts: QStandardPaths.FontsLocation,
    Location.applications: QStandardPaths.ApplicationsLocation,
    Location.music: QStandardPaths.MusicLocation,
    Location.movies: QStandardPaths.MoviesLocation,
    Location.pictures: QStandardPaths.PicturesLocation,
    Location.temp: QStandardPaths.TempLocation,
    Location.home: QStandardPaths.HomeLocation,
    Location.data: QStandardPaths.DataLocation,
    Location.cache: QStandardPaths.CacheLocation,
    Location.generic_data: QStandardPaths.GenericDataLocation,
    Location.runtime: QStandardPaths.RuntimeLocation,
    Location.config: QStandardPaths.ConfigLocation,
    Location.download: QStandardPaths.DownloadLocation,
    Location.generic_cache: QStandardPaths.GenericCacheLocation,
    Location.generic_config: QStandardPaths.GenericConfigLocation,
}

optional_values = {
    # New in Qt 5.4.
    'app_data': 'AppDataLocation',
    'app_local_data': 'AppLocalDataLocation',
}
for key, value in optional_values.items():
    try:
        convert_table[Location[key]] = getattr(QStandardPaths, value)
    except AttributeError:
        pass


class PyStandardPathsTests(unittest.TestCase):

    def setUp(self):
        self.app = QCoreApplication(sys.argv)
        self.app.setApplicationName('Yksom')
        self.app.setOrganizationName('uranusjr')
        configure(application_name='Yksom', organization_name='uranusjr')

    def test_get_writable_path(self):
        for t in Location:
            path = get_writable_path(t)
            self.assertIsInstance(path, pathlib.Path)
            try:
                c = convert_table[t]
            except KeyError:
                print('Key {} not supported by PyQt5. Skipped.'.format(t.name))
                continue
            self.assertEqual(
                path.as_posix(), QStandardPaths.writableLocation(c),
                msg='{}, {}'.format(t.name, c),
            )

    def test_get_standard_paths(self):
        for t in Location:
            try:
                c = convert_table[t]
            except KeyError:
                print('Key {} not supported by PyQt5. Skipped.'.format(t.name))
                continue
            standard_locations = QStandardPaths.standardLocations(c)
            if platform.system() == 'Darwin':   # pragma: no cover
                # Exclude bundle path on OS X. See comments in
                # `get_standard_paths` implementation for more information.
                standard_locations = [
                    loc for loc in standard_locations
                    if not loc.endswith('.app/')
                ]
            elif platform.system() == 'Windows':    # pragma: no cover
                # Exclude paths relative to executable. See comments in
                # `get_standard_paths` implementation for more information.
                app_dir = QCoreApplication.applicationDirPath()
                app_dir_data = '/'.join([app_dir, 'data'])
                standard_locations = [
                    loc for loc in standard_locations
                    if loc not in (app_dir, app_dir_data,)
                ]
            for path in get_standard_paths(t):
                self.assertIsInstance(path, pathlib.Path)
            self.assertEqual(
                [path.as_posix() for path in get_standard_paths(t)],
                standard_locations,
                msg='{}, {}'.format(t.name, c),
            )
