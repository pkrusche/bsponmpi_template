###############################################################################
# Copyright (C) 2007   Peter Krusche, The University of Warwick         
# peter@dcs.warwick.ac.uk                                
###############################################################################

import os
import os.path
import glob
import re
import platform;

from SCons.Defaults import *

###############################################################################
# Modular helpers
###############################################################################

import xscons.bsponmpi
import xscons.tbb
import xscons.blas
import xscons.boost
import xscons.autoconfig

###############################################################################
# read options and configure directories
###############################################################################

optfilename = 'opts.py'

# Try to find options file based on hostname
optfilename_local = 'opts_'+platform.uname()[1]+'_'+platform.uname()[0]+'_'+platform.uname()[4]+'.py'
if len(glob.glob(optfilename_local)) > 0:
    optfilename = optfilename_local
else:
    print 'To use specific options for this system, use options file "'+optfilename_local+'"'

print 'Using options from ' + optfilename

subarch = platform.uname()[4]
opts = Variables(optfilename)

# these are the options that can be specified through the command line
opts.AddVariables(
	EnumVariable('mode', 'Build mode: set to debug or release', 'debug',
                  allowed_values = ('debug', 'release'),
                  ignorecase = 1),
	BoolVariable('profile', 'Enable profiling. Also enables debug information.', 0),
	BoolVariable('runtests', 'Run tests.', 0),
	BoolVariable('debuginfo', 'Include debug information also in release version.', 1),
	('toolset', 'Specify compiler and linker tools: msvc|gnu|intel', 'gnu'),
	('additional_lflags', 'Additional linker flags', ''),
	('additional_cflags', 'Additional compiler flags', ''),
	('mpiexec', 'MPI exec command for testing', 'mpiexec'),
	('mpiexec_params', 'MPI exec parameters for testing', '-n 3')
	)

SCons.Defaults.DefaultEnvironment(tools = [])

# read options before creating root environment
readopts = Environment(tools = [], options = opts)

###############################################################################
# Set up the root environment
###############################################################################

toolset = readopts['toolset']

if toolset == 'msvc':
	ttools = ['msvc', 'mslib', 'mslink']
elif toolset == 'gnu':
	ttools = ['gnulink', 'gcc', 'g++', 'ar']
elif toolset == 'intel':
	ttools = ['icc', 'ilink', 'intelc' ,'ar']
elif toolset == 'intel_windows':
	ttools = ['ilink', 'icl', 'mslib']
else:
	print "[W] Unknown toolset " + toolset + ", using default tools"
	ttools = ['default']

## add included options
xscons.bsponmpi.MakeOptions(opts)
xscons.boost.MakeOptions(opts)
xscons.tbb.MakeOptions(opts)
xscons.blas.MakeOptions(opts)

root = Environment(
    tools = ttools,
    options = opts,
)

# load toolset specific implementation of PrepareEnv
SConscript ('xscons/toolsets/'+toolset+'.py')

Help(opts.GenerateHelpText(root))

###############################################################################
# Setup compiling parameters
###############################################################################

root.Append(
	ENV = os.environ,
	BINDIR = "#bin",
	LIBDIR = "#lib",
	SRCDIR = "#src",
)

# dependency optimization
root.SetOption('max_drift', 4)
root.SetOption('implicit_cache', 1)
root.SetOption('diskcheck', None)
root.Ignore('', '')

platform_name = platform.uname()[0]
platform = ARGUMENTS.get('OS', root['PLATFORM'])

mode = root['mode']
profile = root['profile']
debuginfo = root['debuginfo']
runtests = root['runtests']

root.Append(
	CCFLAGS = ' $CFLAGS',
	CPPPATH = ['#include', '#src'],
	LIBPATH = ['#lib'],
)

###############################################################################
# Setup debug / release mode flags
###############################################################################

Import ('PrepareEnv')
PrepareEnv(root)

###############################################################################
# Setup Boost, TBB and MPI library linking
###############################################################################

xscons.tbb.MakeEnv(root)
xscons.bsponmpi.MakeEnv(root)
xscons.boost.MakeEnv(root)
xscons.blas.MakeEnv(root)

## additional flags not covered by any of the above
root.Append ( 
	LINKFLAGS = root['additional_lflags'],
	CCFLAGS = root['additional_cflags'] 
)

###############################################################################
# Automatic configuration code
###############################################################################

sequential = 0
threadsafe = 0

def ConfRunner(conf, autohdr):
	if not conf.CheckBSPONMPI():
		print "I could not find bsponmpi. Have a look at xscons/bsponmpi.py"
	if not conf.CheckBoost('1.40'):
		print "I could not find Boost >= 1.40. Have a look at xscons/boost.py"
	if not conf.CheckTBB(3):
		print "I could not find Intel TBB version >= 3.0. Have a look at xscons/tbb.py"
	if not conf.CheckBLAS():
		print "No version of BLAS was found"
	else:
		print "BLAS Support enabled"
                autohdr.write("""
#define _HAVE_CBLAS
""")

xscons.autoconfig.AutoConfig ( root, ConfRunner, { 
	'CheckBoost' : xscons.boost.Check,
	'CheckBSPONMPI' : xscons.bsponmpi.Check,
	'CheckTBB' : xscons.tbb.Check,
	'CheckBLAS' : xscons.blas.Check,
	} )

###############################################################################
# Set up unit testing
###############################################################################

def builder_unit_test(target, source, env):	
	app = str(source[0].abspath)
	if os.spawnl(os.P_WAIT, app, app) == 0:
		open(str(target[0]),'w').write("PASSED\n")
	else:
		return 1

def builder_unit_test_mpi(target, source, env):
	# for MPI tests, we run with these processor counts
	
	mpiexec = env["mpiexec"]
	mpiexec_params = env["mpiexec_params"]

	app = str(source[0].abspath)
	runme = mpiexec + " " + mpiexec_params + ' "' + app + '" > ' + str(target[0]) 

	print "Test: running " + runme

	if os.system(runme) == 0:
		open(str(target[0]),'a').write("PASSED\n")
	else:
		return 1

# Create a builder for tests
if sequential:
	bld = Builder(action = builder_unit_test)
	root.Append(BUILDERS = {'Test' :  bld})
else:
	bld = Builder(action = builder_unit_test_mpi)
	root.Append(BUILDERS = {'Test' :  bld})

Export(['root', 'runtests'])

###############################################################################
# get SConscript
###############################################################################

SConscript('src/SConscript')
