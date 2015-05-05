========
Usage
========

Basic Use
----------

All functionalities of PyStandardPaths can be accessed by

::

    import standardpaths

The first thing you need to do is to tell PyStandardPaths about your application::

    standardpaths.configure(application_name='Pepsi', organization_name='Tzu-ping Chung')

Both application and organization names can be left empty, which is useful if you want to configure PyStandardPaths to access "organization-wide" settings that can be shared between multiple applications of your organization.

To get a path that you can write things into, you can use :func:`.get_writable_path`. For example, to get the current user’s Desktop::

    path = standardpaths.get_writable_path('desktop')

This will return a :class:`pathlib.Path` object, pointing to the desktop directory, e.g. `/Users/uranusjr/Desktop` on my Mac.

To get a list of paths to look for files in a system, use :func:`.get_standard_paths`. Taking my Mac as an example again, this prints a list of cache directories for my Pepsi application::

    >>> for path in standardpaths.get_standard_paths('fonts'):
    ...     print(str(path))
    ...
    /Users/uranusjr/Library/Caches/Tzu-ping Chung/Pepsi
    /Library/Caches/Tzu-ping Chung/Pepsi

For a complete list of locations you can use, refer to the documentation of :class:`.Location`.


Advanced Use
-------------

Both :func:`.get_writable_path` and :func:`.get_standard_paths` take an optional second argument `config` that overrides the global configuration. Useful for accessing directories owned by *another* application::

    >>> config = standardpaths.Config(organization_name='M05', application_name='<Y')
    >>> print(standardpaths.get_writable_path('cache', config=config))
    PosixPath('/home/uranusjr/.cache/M05/<Y')

Instead of using strings, you can also use a :class:`.Location` :mod:`enum` value as the first argument::

    path = standardpaths.get_writable_path(standardpaths.Location.applications)
