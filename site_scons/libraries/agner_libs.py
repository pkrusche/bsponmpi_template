import platform
import os.path

###############################################################################
# Setup linking with Agner Fog's libraries (asmlib and vectorclass)
###############################################################################

###############################################################################
# Check for presence of libraries in a config context
###############################################################################

def check(context):       
	context.Message('Checking for Agner Fog\'s libraries ')

	ret = 0

	if context.env['veclibdir']:
		rret = context.TryRun("""
#include "vectorclass.h"
#include <cassert>
#include <cmath>

int main() 
{
    Vec8f a;  
    
    float q[8];					
    
    for(int i = 0; i < 8; ++i) {
    	q[i] = 0.1;
    }

    a.load(q);

    float f2 = horizontal_add(a);          // return sum of 8 elements

    assert(fabs(f2-0.8) < 0.001);

    return 0;
}
""", '.cpp')
		if rret:
			context.Message(' veclib(y) ')
		else:
			context.Message(' veclib(n) ')
		ret += 1
	if context.env['asmlibdir']:
		rret = context.TryRun("""
#include "asmlib.h"
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <cassert>

int main() 
{
	char c1[10], c2[10];
	int i = 0;

	memset(c1, 1, 10);
	memset(c2, 0, 10);

	A_memcpy(c2, c1, 10);

	for(i = 0; i < 10; ++i) {
		assert(c2[i] == 1);
	}

    return 0;
}
""" , '.cpp')
		if rret:
			context.Message(' asmlib(y) ')
		else:
			context.Message(' asmlib(n) ')
		ret += 2
	context.Result(ret)	
	return ret

def make_options (opts):
	arch   = platform.uname()[0]
	if arch == 'Windows':
		opts.AddVariables(
	    	('veclibdir', 'Path to Agner Fog\'s vector library', os.path.abspath('..\\vectorclass')),
	    	('asmlibdir', 'Path to Agner Fog\'s assembler library', os.path.abspath('..\\asmlib')),
		)
	else:
		opts.AddVariables(
	    	('veclibdir', 'Path to Agner Fog\'s vector library', os.path.abspath('../vectorclass')),
	    	('asmlibdir', 'Path to Agner Fog\'s assembler library', os.path.abspath('../asmlib')),
		)

###############################################################################
# Add libraries to an enviroment
###############################################################################

def generate (root):
	arch   = str(platform.uname()[0]).lower()
	subarch = platform.uname()[4]
	bitness = platform.architecture()[0]
	
	if arch == 'darwin' and bitness == '64bit':
		subarch = 'x86_64'
	
	subarch = platform.uname()[4]
	veclibdir = root['veclibdir']
	asmlibdir = root['asmlibdir']

	if os.path.exists(asmlibdir):
		root.Append(
			CPPPATH = [ asmlibdir ], 
			LIBPATH = [ asmlibdir ], 
			)
		if arch == 'darwin':
			if bitness == '64bit':
				root.Append(
					LIBS = 'amac64'
				)
			else:
				root.Append(
					LIBS = 'amac32'
				)
		elif arch == 'windows':
			if bitness == '64bit':	
				root.Append(
					LIBS = 'libacof64'
				)
			else:
				root.Append(
					LIBS = 'libacof32'
				)
		elif arch == 'linux':
			if bitness == '64bit':	
				root.Append(
					LIBS = 'aelf64'
				)
			else:
				root.Append(
					LIBS = 'aelf32'
				)			
		else:
			print "FIXME: pick a library to link me with on " + arch + " " + bitness + " " + subarch

	if os.path.exists(veclibdir):
		root.Append(
			CPPPATH = [ veclibdir ], 
		)
