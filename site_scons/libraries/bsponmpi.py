import platform
import os.path
import re

from SCons.Variables import BoolVariable

###############################################################################
# Make an MPI environment
###############################################################################

def check(context):
	context.Message("Checking for bsponmpi... ")
	ret = 0
	(ret, strn) = context.TryRun("""
#include <iostream>
#include "bsp_config.h"

int main(int argc, char ** argv) {
	using namespace std;
#ifdef _NO_MPI
	cout << "NOMPI" << endl;
#else
	cout << "MPI" << endl;
#endif
#ifdef BSP_THREADSAFE
	cout << "MT" << endl;
#endif
	return 0;
}
""", '.cpp')
	bspv = re.sub("[\n\r\s]", "", strn)

	root = context.env
	arch   = platform.uname()[0]
	subarch   = platform.uname()[4]
	sequential = 1

	libsuffix = 'bsponmpi'

	if bspv == 'MPIMT':
		sequential = 0
		threadsafe = 1
	elif bspv == 'NOMPIMT':
		sequential = 1
		threadsafe = 1
	elif bspv == 'NOMPI':
		sequential = 1
		threadsafe = 0
	elif bspv == 'MPI':
		sequential = 0
		threadsafe = 0		
	else:
		context.Message('Unknown version of bsponmpi library/library not found: ' + bspv + " ")
		context.Result(0)	
		return

	if sequential:
		libsuffix += 'nompi'

	if root['mode'] == 'debug':
		libsuffix += '_debug'

	if threadsafe:
		libsuffix += '_mt'

	context.env.Prepend(LIBS=libsuffix)

	if not sequential:
		if arch == 'Windows':
			mpidir = root['MPIDIR']
			
			if os.path.exists (mpidir + "\\lib\\i386\\msmpi.lib"):
				print "Found MSMPI in " + mpidir
				
				## TODO add support for HPC pack here

				root.Append(CPPPATH = mpidir+"\\Include",
					LIBS = ["msmpi.lib", "msmpe.lib"]
				)

				if subarch == 'AMD64':
					root.Append( LIBPATH = mpidir+"\\Lib\\amd64" )
				else:
					root.Append( LIBPATH = mpidir+"\\Lib\\i386" )
			else:
				print "Found other MPI in " + mpidir
				root.Append( CPPPATH = mpidir+"\\include",
					LIBPATH = mpidir+"\\lib" ,
					LIBS = ["mpi", "mpi_cxx"]
				)
		else:
			root.Replace(
				CXX = root['MPICXX'],
				LINK = root['MPILINK'],
				CC = root['MPICC']
			)
	if not sequential and ret:
		ret = 2
	if sequential and ret:
		ret = 1
		
	context.Message("found " + bspv + " ")
	context.Result(ret)

	return bspv

###############################################################################
# Add MPI Options
###############################################################################

def make_options(opts):
	arch   = platform.uname()[0]
	if arch == 'Windows':
		opts.AddVariables(
			('bsponmpidir', 'Path to bsponmpi', os.path.abspath('..\\bsponmpi')),
			('MPIDIR', 'Path to Microsoft Compute Cluster Pack in Win32', 'C:\\Program Files\\Microsoft Compute Cluster Pack'),
		)
	else:
		opts.AddVariables(
			('bsponmpidir', 'Path to bsponmpi', os.path.abspath('../bsponmpi')),
			('MPICC', 'MPI C compiler wrapper (Unix only)', 'mpicc'),
			('MPICXX', 'MPI C++ compiler wrapper (Unix only)', 'mpicxx'),
			('MPILINK', 'MPI linker wrapper (Unix only)', 'mpicxx'),
		)

###############################################################################
# Make an MPI-capable environment
###############################################################################

def generate(root):
	bspdir = root['bsponmpidir']
	root.Append( LIBPATH = os.path.join(bspdir, 'lib') )
	root.Append( CPPPATH = os.path.join(bspdir, 'include') )
	root.Append( CXXPATH = os.path.join(bspdir, 'include') )
	root.Append( CPATH = os.path.join(bspdir, 'include') )
