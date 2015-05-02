#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implementation for systems compatibile to Free Desktop. Based on
`qstandardpaths_unix.cpp`.
"""

import collections
import logging
import os
import pathlib
import pwd
import re
import stat
import tempfile

from .base import Location, LocationError, _append_org_and_app


logger = logging.getLogger('standardpaths')

RAISE = object()


def _get_path_str(environ_name, default):
    # http://standards.freedesktop.org/basedir-spec/latest/
    path_str = os.getenv(environ_name, default)
    if path_str is RAISE:
        raise KeyError(environ_name)
    return path_str


def _get_path(environ_name, default):
    path_str = _get_path_str(environ_name, default)
    return pathlib.Path(os.path.expanduser(path_str))


def _get_xdg_data_dirs():
    xdg_data_dirs = os.getenv('XDG_DATA_DIRS')
    if not xdg_data_dirs:
        paths = [pathlib.Path('/usr/local/share'), pathlib.Path('usr/share')]
    else:
        paths = list(collections.OrderedDict.fromkeys([
            pathlib.Path(os.path.normpath(ps))
            for ps in xdg_data_dirs.split(':') if ps and os.path.isabs(ps)
        ]).keys())
    return paths


def get_writable_path(location, config=None):
    # TODO: Make sure these fit Qt's implementation.
    if location == Location.home:
        return pathlib.Path(os.path.expanduser('~'))
    if location == Location.temp:
        return pathlib.Path(tempfile.gettempdir())

    if location == Location.generic_cache:
        return _get_path('XDG_CACHE_HOME', '~/.cache')
    if location == Location.cache:
        path = get_writable_path(Location.generic_cache)
        return _append_org_and_app(path, config)
    if location == Location.generic_data:
        return _get_path('XDG_DATA_HOME', '~/.local/share')
    if location in (Location.app_data, Location.app_local_data,):
        path = get_writable_path(Location.generic_data)
        return _append_org_and_app(path, config)
    if location in (Location.config, Location.generic_config,):
        return _get_path('XDG_CONFIG_HOME', '~/.config')
    if location == Location.log:
        # Free Desktop does not provide any suggestions on where log files
        # should be placed, and there is no consensus in the community. Debian
        # has a proposal for this, but nobody really does it. I'm personally in
        # the "log files are not essential" camp, and agrees that it belongs
        # better with cache than data.
        # http://stackoverflow.com/a/27965014/1376863
        return get_writable_path(Location.cache) / 'log'
    if location == Location.runtime:
        username = pwd.getpwuid(os.geteuid()).pw_name
        try:
            path = _get_path('XDG_RUNTIME_DIR', RAISE)
        except KeyError:
            path = get_writable_path(Location.temp) / ('runtime-' + username)
            if not path.exists():
                path.mkdir()
            logger.warning(
                "XDG_RUNTIME_DIR not set, defaulting to '{}'".format(
                    path.as_posix(),
                ),
            )
        if path.owner() != username:
            raise LocationError(
                "Wrong ownership on runtime directory '{path}', "
                "{real} instead of {expected}".format(
                    path=path.as_posix(), real=path.owner(), expected=username,
                ),
            )
        permissions = path.stat().st_mode & 0o777
        if permissions != stat.S_IRWXU:
            path.chmod(stat.S_IRWXU)
        return path

    if location == Location.applications:
        return get_writable_path(Location.generic_data) / 'applications'

    # http://www.freedesktop.org/wiki/Software/xdg-user-dirs
    try:
        key = {
            Location.desktop: 'DESKTOP',
            Location.documents: 'DOCUMENTS',
            Location.pictures: 'PICTURES',
            Location.music: 'MUSIC',
            Location.movies: 'VIDEOS',
            Location.download: 'DOWNLOAD',
        }[location]
    except KeyError:
        pass
    else:
        value = None
        user_dirs = get_writable_path(Location.config) / 'user-dirs.dirs'
        with user_dirs.open() as f:
            xdg_dir_pat = re.compile(r'^XDG_(.*)_DIR=(.*)\s*$')
            for line in f:
                match = xdg_dir_pat.match(line)
                if match and match.group(1) == key:
                    value = match.group(2).strip('"')
                    if value:
                        return pathlib.Path(os.path.expandvars(value))

    try:
        return get_writable_path(Location.home) / {
            Location.desktop: 'Desktop',
            Location.documents: 'Documents',
            Location.pictures: 'Pictures',
            Location.music: 'Music',
            Location.movies: 'Videos',
            Location.download: 'Downloads',
            Location.fonts: '.fonts',
        }[location]
    except KeyError:
        pass

    return pathlib.Path()


def get_standard_paths(location, config=None):
    paths = [get_writable_path(location, config)]
    if location in (Location.config, Location.generic_config,):
        return paths + [
            pathlib.Path(ps)
            for ps in _get_path_str('XDG_CONFIG_DIRS', '/etc/xdg').split(':')
        ]
    if location == Location.generic_data:
        return paths + _get_xdg_data_dirs()
    if location == Location.applications:
        return paths + [path / 'applications' for path in _get_xdg_data_dirs()]
    if location in (Location.app_data, Location.app_local_data):
        return paths + [
            _append_org_and_app(path, config) for path in _get_xdg_data_dirs()
        ]
    return paths
