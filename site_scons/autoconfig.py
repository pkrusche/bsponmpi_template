###############################################################################
# Copyright (C) 2013   Peter Krusche, The University of Warwick         
# pkrusche@gmail.com
###############################################################################

import platform
import pkgutil
import libraries

###############################################################################
# Automatic configuration code
###############################################################################

"""Autoconfig function

Sets up a generic autoconf header. 

This also incudes some generic assertion and stack dump code.

@param root an environment to use
@param customtests a set of custom tests to use for the config enviroment
       (this is populated with all things from the libraries package)
"""

def autoconfig (root, customtests = {}):	
	platform_name = platform.uname()[0]
	subarch = platform.uname()[4]

	conf_libs = [name for _, name, _ in pkgutil.iter_modules(libraries.__path__)]

	conflib_modules = {}
	
	for p in conf_libs:
		conflib_modules[p] = __import__ ("libraries." + p, fromlist = [''])
		customtests[p] = getattr(conflib_modules[p], 'check')

	conf = root.Configure(custom_tests = customtests)
	
	autohdr = open("src/autoconfig.h", 'w')

	# configure environment
	print "Performing autoconfiguration for " + platform_name + "/" + subarch
	autohdr.write("""
/**
 * @file autoconfig.h
 * @brief Automatically generated configuration file.
 */

/*
 * This file is generated automatically and will be overwritten whenever the code is built.
 */ 
#ifndef __AUTOCONFIG_H__
#define __AUTOCONFIG_H__

""")
	
	if root['mode'] == 'debug':
		autohdr.write("""

#ifdef ASSERT
#undef ASSERT
#endif

#ifndef ASSERT

#ifdef _MSC_VER

#include <cassert>
#define ASSERT(x) do { assert(x); } while(0)

#else

#include <execinfo.h>

/** enable dladdr */
#include <dlfcn.h>		// for dladdr
#include <cxxabi.h>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <iostream>
#include <sstream>
 
// This function produces a stack backtrace with demangled function & method names.
static inline void cpp_backtrace() {
	void *callstack[128];
	const int nMaxFrames = sizeof(callstack) / sizeof(callstack[0]);
	char buf[1024];
	int nFrames = backtrace(callstack, nMaxFrames);
	char **symbols = backtrace_symbols(callstack, nFrames);
//  This always works
// 	backtrace_symbols_fd(callstack, nFrames, 2);

	for (int i = 0; i < nFrames; i++) {
		Dl_info info;
		if (dladdr(callstack[i], &info) && info.dli_sname) {
			char *demangled = NULL;
			int status = -1;
			if (info.dli_sname[0] == '_')
				demangled = abi::__cxa_demangle(info.dli_sname, NULL, 0, &status);
			snprintf(buf, sizeof(buf), "%-3d %*p %s + %zd\\n",
					 i, int(2 + sizeof(void*) * 2), callstack[i],
					 status == 0 ? demangled :
					 info.dli_sname == 0 ? symbols[i] : info.dli_sname,
					 (char *)callstack[i] - (char *)info.dli_saddr);
			free(demangled);
		} else {
			snprintf(buf, sizeof(buf), "%-3d %*p %s\\n",
					 i, int(2 + sizeof(void*) * 2), callstack[i], symbols[i]);
		}
		std::cerr << buf;
//		char syscom[256];
//		sprintf(syscom,"addr2line %p -e sighandler", callstack[i]); //last parameter is the name of this app
//		system(syscom);		
	}
	free(symbols);
	if (nFrames == nMaxFrames) {
		std::cerr << "[truncated]\\n";
	}
}

#define ASSERT(x) do { if(!(x) ) { _assert_handler(-1, __FILE__, __LINE__); } } while(0)

static inline void _assert_handler(int sig, const char * file, int line) {
	// print out all the frames to stderr
	if(sig == -1) {
		fprintf(stderr, "Error: assertion failed at %s:%i\\n", file, line);
	} else {
		fprintf(stderr, "Error: signal %d at %s:%i\\n", sig, file, line);	
	}
    std::cerr << "stack trace:" << std::endl;
    cpp_backtrace();
    exit(1);
}

#endif

#endif

""")
	else:
		autohdr.write("""

#ifndef ASSERT
#define ASSERT(x)
#endif

""")

	for t in customtests:
		fn = getattr(conf, t)
		if not fn():
			print "I could not find %s -- have a look at %s" % (str(t), conflib_modules[t].__file__)
			autohdr.write("""
#define _NO_%s

""" % t.upper())
		else:
			autohdr.write("""
#define _HAVE_%s

""" % t.upper())			

	autohdr.write("""

#include <climits>
#include <limits>
#ifndef DBL_EPSILON
#define DBL_EPSILON (std::numeric_limits<double>::epsilon())
#endif


#ifdef _MSC_VER

/** otherwise: no M_PI */
#define _USE_MATH_DEFINES 

#define log2(x) (log(x)/log(2.0))

#include <boost/math/special_functions/fpclassify.hpp> 

namespace std {

	template <class _f>
	static inline bool isnan(_f x) {
		return boost::math::isnan(x); 
	}
};

#endif

#endif /* __AUTOCONFIG_H__ */
""")


	root = conf.Finish()
	autohdr.close()

"""Make autoconf options for all library modules

@param opts : the options object (see SCons docs)
""" 

def make_options(opts):
	conf_libs = [name for _, name, _ in pkgutil.iter_modules(libraries.__path__)]
	
	for p in conf_libs:
		optsfn = getattr(__import__("libraries.%s" % p, fromlist = ['']), 'make_options')
		optsfn(opts)

"""Apply to environment after option reading

@param env : the options object (see SCons docs)
""" 

def generate_env(env):
	conf_libs = [name for _, name, _ in pkgutil.iter_modules(libraries.__path__)]
	
	for p in conf_libs:
		genfn = getattr(__import__("libraries.%s" % p, fromlist = ['']), 'generate')
		genfn(env)
