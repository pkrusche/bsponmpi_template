import os.path
import platform
import glob
import re

###############################################################################
# Setup Boost library 
###############################################################################

###############################################################################
# Check for presence of boost in a config context
###############################################################################

def check(context):
	version = context.env['boost_minversion']
    # Boost versions are in format major.minor.subminor
	v_arr = version.split(".")
	version_n = 0
	if len(v_arr) > 0:
		version_n += int(v_arr[0])*100000
	if len(v_arr) > 1:
		version_n += int(v_arr[1])*100
	if len(v_arr) > 2:
		version_n += int(v_arr[2])
        
	context.Message('Checking for Boost version >= %s... ' % (version))

	ret = context.TryCompile("""
#include <boost/version.hpp>

#if BOOST_VERSION < %d
#error Installed boost is too old!
#endif
    int main() 
    {
        return 0;
    }
    """ % version_n, '.cpp')
	context.Result(ret)
	return ret

###############################################################################
# Add Boost-specific options
###############################################################################

def make_options(opts):
    arch   = platform.uname()[0]
    if arch == 'Windows':    
		opts.AddVariables (
		    ('boostdir', 'Path to Boost library in Win32', 'C:\\Boost\\include') )
    else:
		opts.AddVariables (
		    ('boostdir', 'Path to Boost library (empty by default)', '') )

    opts.AddVariables (
	    ('boost_minversion', 'Minimum acceptable version of Boost', '1.53'),
	    ('boostlibs', 'Boost libraries to link with, separated by comma/whitespace/colon', 'boost_program_options')
	)

###############################################################################
# Find boost and add to environment
###############################################################################

def generate ( env ):
    boost_include = ''
    boost_lib = ''
    boostdir = env['boostdir']

	# see if we can find boost on Windows
    arch   = platform.uname()[0]
    if arch == 'Windows':    
	    dirs = glob.glob(boostdir+"\\*")
	    if len(dirs) > 0:
	    	dirs.sort()
	    	boost_include = dirs[len(dirs) - 1]
	    	boost_lib = boostdir+"\\..\\lib"

	    # boost include path must go into CCFLAGS because the scons include dependency
	    # parser may die otherwise
	    if env['toolset'] == 'msvc' or env['toolset'] == 'intel_windows':
			env.Append(
				CPPFLAGS = '/I'+boost_include ,
				LIBPATH = [ boost_lib ],
			)
    else:
    	if boostdir != '':
    		boost_include = os.path.join(boostdir, 'include')
    		boost_lib = os.path.join(boostdir, 'include')
    		if not os.path.exists(boost_include):
    			boost_include = ''
    		if not os.path.exists(boost_lib):
    			boost_lib = ''
    	if boost_include != '':
			env.Append(
				CPPFLAGS = ' -I'+boost_include )
			boost_lib = os.path.join(boost_include, '..', 'lib')

    	if boost_lib:
    		if arch == 'Darwin':
    			if not 'TEST_ENV' in env:
    				env['TEST_ENV'] = dict()
    			if 'DYLD_LIBRARY_PATH' in env['TEST_ENV']:
    				env['TEST_ENV']['DYLD_LIBRARY_PATH'] += ':'+boost_lib
    			else:
    				env['TEST_ENV']['DYLD_LIBRARY_PATH'] = boost_lib
			env.Append(
				LIBPATH = [ boost_lib ] )

    	blibs = []
    	blibs.extend(re.split('[\s\n\r\:,]+', env['boostlibs']))
    	env.Append(	LIBS = blibs  )
