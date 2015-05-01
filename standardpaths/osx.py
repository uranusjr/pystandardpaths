#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implementation for OS X. Based on `qstandardpaths_mac.mm`.
"""

import ctypes
import ctypes.util
import os.path
import pathlib
import tempfile

from rubicon.objc import ObjCClass

from .base import Location, LocationError, _append_org_and_app


class FSRef(ctypes.Structure):
    _fields_ = [('hidden', ctypes.c_uint8 * 80)]


def _bti(bs):
    """Convert multibyte character literals in C enum to int value.

    See 6.4.4.4 in C99 (TC3).
    http://stackoverflow.com/a/548312/1376863
    """
    rbs = reversed(bytearray(bs))
    return sum(b * (2 ** (i * 8)) for b, i in zip(rbs, range(len(bs))))


def _load(name):
    return ctypes.cdll.LoadLibrary(ctypes.util.find_library(name))


# CoreServices/CarbonCore/Folders.h
kOnAppropriateDisk  = -32767
kUserDomain         = -32763

# CoreServices/CarbonCore/Folders.h
kApplicationsFolderType         = _bti(b'apps')
kApplicationSupportFolderType   = _bti(b'asup')
kCachedDataFolderType           = _bti(b'cach')
kDesktopFolderType              = _bti(b'desk')
kDocumentsFolderType            = _bti(b'docs')
kFontsFolderType                = _bti(b'font')
kMovieDocumentsFolderType       = _bti(b'mdoc')
kMusicDocumentsFolderType       = 0xb5646f63  # 'µdoc'
kPictureDocumentsFolderType     = _bti(b'pdoc')
kPreferencesFolderType          = _bti(b'pref')
kTemporaryFolderType            = _bti(b'temp')

# Foundation/NSPathUtilities.h
NSDownloadsDirectory = 15
NSUserDomainMask = 1


def _get_path(location, domain, config):
    """Re-implementation of `macLocation`.
    """
    if location == Location.download:
        _load('Foundation')     # Needed by Rubicon.
        manager = ObjCClass('NSFileManager').defaultManager()
        error = ObjCClass('NSError').alloc().init()
        url = manager.URLForDirectory_inDomain_appropriateForURL_create_error_(
            NSDownloadsDirectory, NSUserDomainMask, None, False,
            ctypes.byref(error.__dict__['ptr']),
        )
        if not url:
            raise LocationError('Could not resolve {}: {}'.format(
                location.name, error.localizedDescription(),
            ))
        return pathlib.Path(url.path)

    CoreServices = _load('CoreServices')
    folder_type = {
        Location.config: kPreferencesFolderType,
        Location.generic_config: kPreferencesFolderType,
        Location.desktop: kDesktopFolderType,
        Location.documents: kDocumentsFolderType,
        Location.fonts: kFontsFolderType,
        Location.applications: kApplicationsFolderType,
        Location.music: kMusicDocumentsFolderType,
        Location.movies: kMovieDocumentsFolderType,
        Location.pictures: kPictureDocumentsFolderType,
        Location.temp: kTemporaryFolderType,
        Location.generic_data: kApplicationSupportFolderType,
        Location.runtime: kApplicationSupportFolderType,
        Location.app_data: kApplicationSupportFolderType,
        Location.app_local_data: kApplicationSupportFolderType,
        Location.generic_cache: kCachedDataFolderType,
        Location.cache: kCachedDataFolderType,
    }.get(location, kDesktopFolderType)
    fsref = FSRef()
    r = CoreServices.FSFindFolder(
        domain, folder_type, False, ctypes.byref(fsref),
    )
    if r:
        raise LocationError('Could not resolve {}: {}'.format(
            location.name, r,
        ))

    # TODO: Make this more bullet-proof.
    string = ctypes.create_string_buffer(1024)
    r = CoreServices.FSRefMakePath(ctypes.byref(fsref), string, 1024)
    if r:
        raise LocationError('Could not resolve {}: {}'.format(
            location.name, r,
        ))
    path = pathlib.Path(string.value.decode('utf-8'))

    if location in (
            Location.app_data, Location.app_local_data, Location.cache,):
        path = _append_org_and_app(path, config)
    return path


def get_writable_path(location, config=None):
    """Re-implementation of `QStandardPaths::writableLocation`
    """
    # TODO: Make sure these fit Qt's implementation.
    if location == Location.home:
        return pathlib.Path(os.path.expanduser('~'))
    if location == Location.temp:
        return pathlib.Path(tempfile.gettempdir())

    domain = {
        Location.generic_data: kUserDomain,
        Location.app_data: kUserDomain,
        Location.app_local_data: kUserDomain,
        Location.generic_cache: kUserDomain,
        Location.cache: kUserDomain,
        Location.runtime: kUserDomain,
    }.get(location, kOnAppropriateDisk)
    return _get_path(location, domain, config)


def get_standard_paths(location, config=None):
    """Re-implementation of `QStandardPaths::standardLocations`
    """
    paths = [get_writable_path(location)]
    if location in (
            Location.generic_data, Location.app_data, Location.app_local_data,
            Location.generic_cache, Location.cache,):
        try:
            path = _get_path(location, kOnAppropriateDisk, config)
        except LocationError:
            pass
        else:
            paths.append(path)

    # Qt supports retrieval of paths inside CFBundle. Python programs are
    # usually not bundled, so we skip these.
    # TODO: Support this if applicable?

    return paths
