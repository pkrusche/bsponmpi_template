BSPONMPI Template C++ Project
=============================

This is a template project which uses SCons to automatically locate [bsponmpi](https://github.com/pkrusche/bsponmpi) and its dependencies. Also, it can test for a few more libraries I found useful.

Setup
-----

At minimum, you will need:

* [SCons](http://www.scons.org/) for making/compiling the project

For writing parallel code, you need:

* The [Boost](http://www.boost.org/) libraries. 
* [Threading Building Blocks](http://threadingbuildingblocks.org/)
* [Bsponmpi](https://github.com/pkrusche/bsponmpi)
* Optionally: a version of MPI (e.g. [OpenMPI](http://www.open-mpi.org/) or [Microsoft HPC Pack](http://msdn.microsoft.com/en-us/library/cc136762(v=vs.85).aspx)) on Windows)

Additionally, you can check for these:

* A version of BLAS [e.g. OpenBLAS](https://github.com/xianyi/OpenBLAS) 
* [Agner Fog's Vectorclass library](http://agner.org/optimize/)
* [MATLAB](http://www.mathworks.co.uk/products/matlab/) : MATLAB, The MathWorks, Inc., Natick, Massachusetts, United States. (for building MEX files/writing MAT files).

You can then compile the project by running

```
$ scons
```

... in the project's checkout folder (make clean using `scons -c`).

The locations of all dependencies can be specified in an options file or on the command line. A straightforward way to get the options file is to copy `opts.py` from bsponmpi.

A summary of all options is shown when running

```
$ scons --help
```

All source code is contained in `src`. An autoconfig header is created in there, too. Also, the `include` directory can contain public API files (make sure these don't depend on the autoconfig header).

Usage
-----

The only files you will hopefully need to modify are `src/SConscript`, and (potentially) an options file (see section below).

In `src/SConscript`, you can add files to your project. By default, we compile `main.cpp` into `bin/main`.

```
Import("root")

root.Program('#bin/main', 'main.cpp')
```

Everything that is compiled using `root` will have access to all libraries which were detected during configuration.

Unit Testing
------------

When setting `runtests=1`, `tests/SConscript` will attempt to build and execute unit tests. All C++ files which have a name starting with `test_` will be compiled and run. If their return value is zero, the test is assumed to have run successfully.

An example is shown in `tests/test_main.cpp`. The compiled test executables go into `bin/unit_tests`.

When running the default version of this project, this should be the output:

```
$ scons runtests=1 mode=release
scons: Reading SConscript files ...
To use specific options for this platform, use options file "opts_Darwin_i386.py"
To use specific options for this system, use options file "opts_naphta.cov.warwick.ac.uk_Darwin_i386.py"
Using options from opts.py
Performing autoconfiguration for Darwin/i386
Checking for bsponmpi... found NOMPIMT (cached) yes
Checking for Boost version >= 1.40... yes
Checking for TBB version >= 3.0... yes
Checking for Agner Fog's libraries  veclib(y)  asmlib(y) (cached) yes
Checking for CBLAS... (cached) no
No version of BLAS was found.  Have a look at xscons/blas.py
scons: done reading SConscript files.
scons: Building targets ...
g++ -o src/main.o -c -g -fast -Iinclude -Isrc -I/Users/peterkrusche/Documents/Code/workspace/bsponmpi/include src/main.cpp
g++ -o bin/main -g src/main.o -Llib -L/Users/peterkrusche/Documents/Code/workspace/bsponmpi/lib -ltbb -ltbbmalloc -lboost_program_options -lbsponmpinompi_mt
g++ -o tests/test_main.o -c -g -fast -Iinclude -Isrc -I/Users/peterkrusche/Documents/Code/workspace/bsponmpi/include tests/test_main.cpp
g++ -o bin/unit_tests/main -g tests/test_main.o -Llib -L/Users/peterkrusche/Documents/Code/workspace/bsponmpi/lib -ltbb -ltbbmalloc -lboost_program_options -lbsponmpinompi_mt
builder_unit_test(["bin/unit_tests/main.passed"], ["bin/unit_tests/main"])
Great success.
scons: done building targets.
```

Options
-------

### General

Options can be specified by means of SCons build variables. These can be given on the command line, e.g. like this:

```
$ scons mode=release
```

This will compile release binaries (with optimisation enabled, ...).

Another way is to create an options file. You can create a file called `opts.py` which looks like this:

```python
mode = 'release'
```

If you have configuration files for different platforms/hosts which you want to store in a repository without overwriting, you can use a platform-specific, or a host-specific options file. SCons will tell you the names of these files when it is run:

```
$ scons
scons: Reading SConscript files ...
To use specific options for this platform, use options file "opts_Darwin_i386.py"
To use specific options for this system, use options file "opts_naphta.cov.warwick.ac.uk_Darwin_i386.py"
...
```

Here is a list of variables you can specify.

* *mode* Build mode: set to debug or release', 'debug',
* *profile*  Enable profiling (Linux). Also enables debug information.
* *runtests*  Run unit tests.
* *debuginfo* Switch to include debug information also in release version, defaults to 1
* *toolset*  Specify compiler and linker tools: msvc|gnu|intel -- see `xscons/toolsets`
* *additional_lflags* and *additional_cflags* these allow you to add additional compiler and linker flags
* *mpiexec* MPI exec command for testing
* *mpiexec_params* MPI exec parameters for testing -- you can specify the number of processors to test on, e.g. using `-n 3`

### [Boost](http://www.boost.org/)

Getting Boost on Linux or Mac OS X is relatively easy, use your favourite package manager, e.g. 

```sudo apt-get install libboost-all-dev```

...or [MacPorts](http://www.macports.org/) on MacOS/X)

On Windows (or if you want the most recent version of Boost), you will need to compile Boost, which may take some time. Once you have compiled Boost, you will need to install it somewhere (see their documentation). On Windows, the default folder is in `C:\\Boost`. The build variable `boostdir` needs to point to the include directory. On Windows, Boost will install different versions in subfolders of the include folder. In `xscons/boost.py`, this is handled by trying to choose the most recent version of Boost.

These options are available in `boost.py`:

* *boostdir* : the include directory for boost. 
* *boost_minversion* : minimum version of Boost required (default: 1.40)
* *boostlibs* Boost libraries to link with, separated by comma/whitespace/colon. Default is `boost_program_options`, because bsponmpi needs this (when setting this option, don't forget to include it if you want to use bsponmpi

### [Threading Building Blocks](http://threadingbuildingblocks.org/)

The easiest way to use TBB is to download the binary distribution for your platform, and point to it in the options file using the `tbbdir` variable e.g. like this:

```python
tbbdir = "Z:\\Peter\\workspace\\tbb40_297oss"
```

On Windows, `tbb.py` will try to automatically figure out which version of the library to link to.

### [Bsponmpi](https://github.com/pkrusche/bsponmpi)

The script `xscons/bsponmpi.py` will try to automatically determine in which mode `bsponmpi` was compiled (this is saved in BSPonMPI's `bsp_config.h`) and link with the right library and MPI if necessary.

Using the variable `bsponmpidir`, you can set the path to bsponmpi (default: `../bsponmpi`)

On Windows, you need to specify the location of Microsoft Compute Cluster Pack using `MPIDIR` (default: 'C:\\Program Files\\Microsoft Compute Cluster Pack').

On other platforms, the easiest way is to use `mpicc` and friends. You can specify these individually using `MPICC`, `MPICXX`, and `MPILINK`.

### BLAS [e.g. OpenBLAS](https://github.com/xianyi/OpenBLAS) 

Using the right version of BLAS will dramatically improve performance (rule of thumb: if the cblas_ddot flop rate is below 1 GFLOP/s for vectors which aren't too short, you're doing something wrong). The config variable `cblas` can specify which version of BLAS we should link to. Possible options are : `none|blas|atlas|openblas|accelerate`. If you require additional library/include paths, you can use the `additional_lflags` and `additional_cflags` variables to add these.

### [Agner Fog's Vector library](http://agner.org/optimize/)

This is a useful library for implementing vector operations using MMX/SSE/AVX (also, there is a library with a faster version of `memcpy`).

You can use the configuration variables `veclibdir` and `asmlibdir` to point to the locations of these libraries (default locations are in `../(asm|vec)libdir`).

### [MATLAB](http://www.mathworks.co.uk/products/matlab/)

In [site_scons/site_tools/mex.py](site_scons/site_tools/mex.py), there is now a simple builder for MEX files. If MATLAB is on your path, it should work out of the box, otherwise, you can set the MATLAB_PATH build variable to the bin directory of your installation e.g. like this:

```bash
$ scons MATLAB_PATH=/Applications/MATLAB_R2012b.app/bin
```

You can then build Mex files like shared libraries by adding the following to a SConscript (see [src/SConscript](src/SConscript) and [src/mex_test.cpp](src/mex_test.cpp) ):

```python

if root['MEX_EXT'] != '':
    root.MEX('#bin/mex_test', 'mex_test.cpp')
```

_Remarks/TODOs:_

* Using boost in MEX files can make trouble. MATLAB ships with a dynamic library version of Boost which may be incompatible with the one you're using (e.g. it appears that the one that comes with R2012b doesn't know about the Bzip2 part in boost::iostreams). To fix such runtime link errors, I found the easiest way is to link boost statically (build boost using `b2 link=static`). Other possible (and more tricky) solutions are:

    *  This one (which I wasn't able to reproduce on MacOS X, but it probably works on Linux): [http://stackoverflow.com/questions/13934107/using-boost-in-matlab-mex-library-different-from-matlabs-version](http://stackoverflow.com/questions/13934107/using-boost-in-matlab-mex-library-different-from-matlabs-version)
    *  Fix rpath manually in the shared object/Mex file after building.
