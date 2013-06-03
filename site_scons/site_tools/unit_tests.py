###############################################################################
# Copyright (C) 2013   Peter Krusche, The University of Warwick         
# pkrusche@gmail.com
###############################################################################

import os
from SCons.Script import *

###############################################################################
# Unit Testing
###############################################################################

"""Unit test builder function
"""
def builder_unit_test(target, source, env):	
	app = str(source[0].abspath)

	xenv = os.environ
	if 'TEST_ENV' in env:
		for k in env['TEST_ENV']:
			xenv[k] = env['TEST_ENV'][k]
	if os.spawnle(os.P_WAIT, app, app, xenv) == 0:
		open(str(target[0]),'w').write("PASSED\n")
	else:
		return 1

"""Unit test builder function which uses MPI
"""
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

"""Set up an environment for using unit testing

@param env : the environment

"""
def generate(env):
	# Create a builder for tests
	if not env['mpiexec']:
		bld = Builder(action = builder_unit_test)
		env.Append(BUILDERS = {'Test' :  bld})
	else:
		bld = Builder(action = builder_unit_test_mpi)
		env.Append(BUILDERS = {'Test' :  bld})

"""Check if environment supports unit testing

@param env : the environment

"""
def exists(env):
	return 1
