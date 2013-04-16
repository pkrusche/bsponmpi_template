BSPONMPI Template C++ Project
=============================

This is a template project which uses SCons to automatically locate [bsponmpi](https://github.com/pkrusche/bsponmpi) and its dependencies.

Setup
-----

You need to get and install all dependencies:

* [SCons](http://www.scons.org/) for making/compiling the project
* The [Boost](http://www.boost.org/) libraries. 
* [Threading Building Blocks](http://threadingbuildingblocks.org/)
* (optionally) a version of BLAS [e.g. OpenBLAS](https://github.com/xianyi/OpenBLAS) 
* [Bsponmpi](https://github.com/pkrusche/bsponmpi)

You can then compile the project using 

```
$ scons -Q mode=release 
```

