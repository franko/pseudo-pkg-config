# Pseudo pkg-config

An unofficial, simple python implementation of pkg-config to be used with MinGW.

The aim of Pseudo pkg-config is to provide a very simple implementation of pkg-config to be used with MinGW on Windows.
It was done because MinGW does not include pkg-config and the official application is not simple to install and it does require additional DLLs.
Pkg-config is very useful to automatically discover installed libraries, query their version and obtains the required compiler and link flags.
In addition pkg-config is often used by the "configure" script and is therefore required to make it works.

Pseudo pkg-config is very simple to install because it consists of **simple Python script** without any requirements other then Python itself.

Pseudo pkg-config implements all the essential features of pkg-config but **not everything** so if you use it be aware that it may fails if
some unusual options are used.
The good thing is that if something is missing it is quite easy to add it by directly modifying the Python script.

Currently Pseudo pkg-config supports the flags ``--cflags``, ``--libs``, ``--exists``, ``--modversion`` and ``--atleast-pkgconfig-version``.
