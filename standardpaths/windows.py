#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implementation for Windows. Based on `qstandardpaths_win.cpp`.
"""

import ctypes
import os.path
import pathlib
import tempfile

from .base import Config, Location, LocationError, _append_org_and_app

__all__ = ['get_writable_path', 'get_standard_paths']


c_bytes_8 = ctypes.c_byte * 8


class GUID(ctypes.Structure):
    _fields_ = [
        ('Data1', ctypes.c_long,),
        ('Data2', ctypes.c_short),
        ('Data3', ctypes.c_short),
        ('Data4', c_bytes_8),
    ]


# http://sourcecodebrowser.com/glib2.0/2.28.0/gutils_8c_source.html
FOLDERID_Downloads = GUID(
    0x374de290, 0x123f, 0x4565,
    c_bytes_8(0x91, 0x64, 0x39, 0xc4, 0x92, 0x5e, 0x46, 0x7b),
)


# http://www.installmate.com/support/im9/using/symbols/functions/csidls.htm
CSIDL_PROGRAMS          = 0x0002
CSIDL_PERSONAL          = 0x0005
CSIDL_MYMUSIC           = 0x000d
CSIDL_MYVIDEO           = 0x000e
CSIDL_DESKTOPDIRECTORY  = 0x0010
CSIDL_FONTS             = 0x0014
CSIDL_APPDATA           = 0x001a
CSIDL_LOCAL_APPDATA     = 0x001c
CSIDL_MYPICTURES        = 0x0027


def _get_path(folder_id):
    string = ctypes.create_unicode_buffer(1024)
    r = ctypes.windll.shell32.SHGetFolderPathW(
        None, folder_id, ctypes.c_int(), 0, string,
    )
    if r:
        raise LocationError(r)
    return pathlib.Path(string.value)


def _get_data_config_path(location, config):
    if location == Location.app_data:
        folder_id = CSIDL_APPDATA           # "Roaming" path.
    else:
        folder_id = CSIDL_LOCAL_APPDATA     # Local path.

    try:
        path = _get_path(folder_id)
    except LocationError as e:
        LocationError('Could not resolve {}: {}'.format(location.name, str(e)))
    path = _append_org_and_app(path, config)
    return path


def get_writable_path(location, config=None):
    """Re-implementation of `QStandardPaths::writableLocation`
    """
    # TODO: Make sure these fit Qt's implementation.
    if location in (Location.home, Location.runtime,):
        return pathlib.Path(os.path.expanduser('~'))
    if location == Location.temp:
        return pathlib.Path(tempfile.gettempdir())

    if location == Location.generic_cache:
        return get_writable_path(Location.generic_data) / 'cache'
    if location == Location.cache:
        return get_writable_path(Location.app_local_data) / 'cache'

    if location == Location.download:
        try:
            SHGetKnownFolderPath = ctypes.windll.shell32.SHGetKnownFolderPath
        except AttributeError:
            pass    # Fallback.
        else:
            # TODO: Make this more bullet-proof.
            string = ctypes.c_wchar_p('\x00' * 1024)
            r = SHGetKnownFolderPath(
                ctypes.byref(FOLDERID_Downloads), 0, None,
                ctypes.byref(string),
            )
            if not r:
                return pathlib.Path(string.value)
            # If this fails, fallback.

    if location in (Location.generic_data, Location.generic_config,):
        return _get_data_config_path(location, Config('', ''))
    if location in (
            Location.app_local_data, Location.app_data, Location.config,):
        return _get_data_config_path(location, config)

    folder_id = {
        Location.applications: CSIDL_PROGRAMS,
        Location.desktop: CSIDL_DESKTOPDIRECTORY,
        Location.documents: CSIDL_PERSONAL,
        Location.download: CSIDL_PERSONAL,  # Fallback for the previous method.
        Location.fonts: CSIDL_FONTS,
        Location.music: CSIDL_MYMUSIC,
        Location.movies: CSIDL_MYVIDEO,
        Location.pictures: CSIDL_MYPICTURES,
    }.get(location, CSIDL_DESKTOPDIRECTORY)
    try:
        return _get_path(folder_id)
    except LocationError as e:
        LocationError('Could not resolve {}: {}'.format(location.name, str(e)))


def get_standard_paths(location, config=None):
    """Re-implementation of `QStandardPaths::standardLocations`
    """
    paths = [get_writable_path(location)]
    if location in (Location.generic_data, Location.generic_config,):
        paths.append(_get_data_config_path(location, Config('', '')))
    if location in (
            Location.app_local_data, Location.app_data, Location.config,):
        paths.append(_get_data_config_path(location, config))

    # Qt adds applicationDirPath() and a subdirectory of it to the config
    # and data paths. This is generally not a good idea for Python scripts,
    # and doesn't work well with package managers, so we skip these.
    # TODO: Support this through a config value?

    return paths
