###############################################################################
# Copyright (C) 2013   Peter Krusche, The University of Warwick         
# pkrusche@gmail.com
###############################################################################

from SCons.Script import *

import os
import os.path
import glob
import platform

###############################################################################
# Modular library helpers
###############################################################################

import autoconfig
import toolsets

"""Make Root Environment

Create a root environment and set up unit tests etc.

This is some patchwork to make SCons work with platform and host-specific
configuration files, and also to allow setting up the toolsets via options.

@param additional_tools : additional tools to add

"""
def make_root_env(additional_tools=[]):

	###############################################################################
	# read options and configure directories
	###############################################################################

	# default options file name
	optfilename = 'opts.py'

	# Options file for current platform
	optfilename_plat = 'opts_'+platform.uname()[0]+'_'+platform.uname()[4]+'.py'

	# Try to find options file based on hostname
	#
	optfilename_local = 'opts_'+platform.uname()[1]+'_'+platform.uname()[0]+'_'+platform.uname()[4]+'.py'
	if len(glob.glob(optfilename_local)) > 0:
	    optfilename = optfilename_local
	# Second choice: platform file
	elif len(glob.glob(optfilename_plat)) > 0:
	    optfilename = optfilename_plat
	else:
	# third choice: stick with opts.py
	    print 'To use specific options for this platform, use options file "'+optfilename_plat+'"'
	    print 'To use specific options for this system, use options file "'+optfilename_local+'"'

	print 'Using options from ' + optfilename

	opts = Variables(optfilename)

	# these are the options that can be specified through the command line
	opts.AddVariables(
		EnumVariable('mode', 'Build mode: set to debug or release', 'debug',
	                  allowed_values = ('debug', 'release'),
	                  ignorecase = 1),
		BoolVariable('profile', 'Enable profiling. Also enables debug information.', 0),
		BoolVariable('runtests', 'Run tests.', 0),
		BoolVariable('debuginfo', 'Include debug information also in release version.', 1),
		('toolset', 'Specify compiler and linker tools: msvc|gnu|clang|intel', 'gnu'),
		('_CXX', 'Replacement CXX', ''),
		('_CC', 'Replacement CC', ''),
		('_LINK', 'Replacement LINK', ''),
		('additional_lflags', 'Additional linker flags', ''),
		('additional_cflags', 'Additional compiler flags', ''),
		('mpiexec', 'MPI exec command for testing', ''),
		('mpiexec_params', 'MPI exec parameters for testing', '-n 3'),
		('MATLAB_PATH', 'Path to Matlab for mex Builder', None),
		('MATLAB_MEX_EXTRA', 'Extra switches for mex compiler.', '')
		)

	SCons.Defaults.DefaultEnvironment(tools = [])

	# read options before creating root environment
	readopts = Environment(tools = [], options = opts)

	###############################################################################
	# Set up the root environment
	###############################################################################

	toolset = readopts['toolset']

	if toolset == 'msvc':
		ttools = ['msvc', 'mslib', 'mslink', 'unit_tests']
	elif toolset == 'gnu' or toolset == 'clang':
		ttools = ['gnulink', 'gcc', 'g++', 'ar', 'unit_tests']
	elif toolset == 'intel':
		ttools = ['icc', 'ilink', 'intelc' ,'ar', 'unit_tests']
	elif toolset == 'intel_windows':
		ttools = ['ilink', 'icl', 'mslib', 'unit_tests']
	else:
		print "[W] Unknown toolset " + toolset + ", using default tools"
		ttools = ['default', 'unit_tests']

	ttools = ttools + additional_tools

	## add included options
	autoconfig.make_options(opts)

	root = Environment(
	    tools = ttools,
	    options = opts,
	)

	# load toolset specific implementation of PrepareEnv
	getattr(__import__('toolsets.%s' % toolset, fromlist = ['']), 'generate')(root)

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

	root.Append(
		CCFLAGS = ' $CFLAGS',
		CPPPATH = ['#include', '#src'],
		LIBPATH = ['#lib'],
	)

	###############################################################################
	# Setup debug / release mode flags
	###############################################################################

	if root['_CXX'] != '':
		root['CXX'] = root['_CXX']
	if root['_CC'] != '':
		root['CC'] = root['_CC']
	if root['_LINK'] != '':
		root['LINK'] = root['_LINK']

	###############################################################################
	# Setup Boost, TBB and MPI library linking
	###############################################################################

	autoconfig.generate_env(root)

	## additional flags not covered by any of the above
	root.Append ( 
		LINKFLAGS = root['additional_lflags'],
		CCFLAGS = root['additional_cflags'] 
	)

	###############################################################################
	# Automatic configuration code
	###############################################################################

	autoconfig.autoconfig( root )

	###############################################################################
	# Set up unit testing
	###############################################################################

	return root
