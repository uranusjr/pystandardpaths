#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enum
import importlib
import platform


class Location(enum.Enum):
    """describes the different locations that can be queried using functions
    such as :func:`.get_writable_path` and :func:`.get_standard_paths`.

    Some of the values in this enum represent a user configuration. Such enum
    values will return the same paths in different applications, so they could
    be used to share data with other applications. Other values are specific to
    this application. Each enum value in the table below describes whether it's
    application-specific or generic.

    Application-specific directories should be assumed to be unreachable by
    other applications. Therefore, files placed there might not be readable by
    other applications, even if run by the same user. On the other hand,
    generic directories should be assumed to be accessible by all applications
    run by this user, but should still be assumed to be unreachable by
    applications by other users.

    Data interchange with other users is out of the scope of PyStandardPaths.
    """

    desktop = 0
    """Returns the user's desktop directory. This is a generic value.
    """

    documents = 1
    """Returns the directory containing user document files. This is a generic
    value. The returned path is never empty.
    """

    fonts = 2
    """Returns the directory containing user's fonts. This is a generic value.
    Note that installing fonts may require additional, platform-specific
    operations.
    """

    applications = 3
    """Returns the directory containing the user applications (either
    executables, application bundles, or shortcuts to them). This is a generic
    value. Note that installing applications may require additional,
    platform-specific operations. Files, folders or shortcuts in this directory
    are platform-specific.
    """

    music = 4
    """Returns the directory containing the user's music or other audio files.
    This is a generic value. If no directory specific for music files exists, a
    sensible fallback for storing user documents is returned.
    """

    movies = 5
    """Returns the directory containing the user's movies and videos. This is a
    generic value. If no directory specific for movie files exists, a sensible
    fallback for storing user documents is returned.
    """

    pictures = 6
    """Returns the directory containing the user's pictures or photos. This is
    a generic value. If no directory specific for picture files exists, a
    sensible fallback for storing user documents is returned.
    """

    temp = 7
    """Returns a directory where temporary files can be stored (the same as
    :func:`tempfile.gettempdir`). The returned value might be
    application-specific, shared among other applications for this user, or
    even system-wide. The returned path is never empty.
    """

    home = 8
    """Returns the user's home directory (the same as
    `os.path.expanduser('~')`). On Unix systems, this is equal to the HOME
    environment variable. This value might be generic or application-specific,
    but the returned path is never empty.
    """

    data = 9
    """Returns the same value as :attr:`.app_local_data`. This enumeration
    value is deprecated. Using :attr:`.app_data` is preferable since on
    Windows, the roaming path is recommended.
    """
    cache = 10
    generic_data = 11
    """Returns a directory location where persistent data shared across
    applications can be stored. This is a generic value. The returned path is
    never empty.
    """

    runtime = 12
    """Returns a directory location where runtime communication files should be
    written, like Unix local sockets. This is a generic value. The returned
    path may be empty on some systems.
    """

    config = 13
    """Returns a directory location where user-specific configuration files
    should be written. This may be either a generic value or
    application-specific, and the returned path is never empty.
    """

    download = 14
    """Returns a directory for user's downloaded files. This is a generic
    value. If no directory specific for downloads exists, a sensible fallback
    for storing user documents is returned.
    """

    generic_cache = 15
    """Returns a directory location where user-specific non-essential (cached)
    data, shared across applications, should be written. This is a generic
    value. Note that the returned path may be empty if the system has no
    concept of shared cache.
    """

    generic_config = 16
    """Returns a directory location where user-specific configuration files
    shared between multiple applications should be written. This is a generic
    value and the returned path is never empty.
    """

    app_data = 17
    """Returns a directory location where persistent application data can be
    stored. This is an application-specific directory. To obtain a path to
    store data to be shared with other applications, use :attr:`.generic_data`.
    The returned path is never empty. On the Windows operating system, this
    returns the roaming path.
    """

    app_local_data = data
    """Returns the local settings path on the Windows operating system. On all
    other platforms, it returns the same value as :attr:`.app_data`.
    """


class LocationError(OSError):
    """Exception class raised to indicate an error during path resolution.
    """


class Config(object):
    """Configuration class that holds application information.

    .. seealso::
        :func:`.configure` and :func:`get_config`.
    """
    def __init__(self, application_name='', organization_name=''):
        self.application_name = application_name
        self.organization_name = organization_name


_config = Config('', '')


def configure(application_name='', organization_name=''):
    """Configure default application information used by PyStandardPaths.

    .. seealso::
        :func:`get_config` and :class:`.Config`.
    """
    global _config
    _config = Config(application_name, organization_name)


def get_config():
    """Get the current configuration of application information.

    :rtype: :class:`.Config`
    """
    return _config


def _append_org_and_app(path, config):
    """Re-implementation of `appendOrganizationAndApp`.
    """
    if config is None:
        config = get_config()
    if config.organization_name:
        path = path / config.organization_name
    if config.application_name:
        path = path / config.application_name
    return path


def _get_implementation():
    module_name = {
        'Darwin': '..osx',
        'Windows': '..windows',
    }.get(platform.system(), '..unix')
    return importlib.import_module(module_name, package=__loader__.name)
