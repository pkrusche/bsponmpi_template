###############################################################################
# Setup BLAS library linking
###############################################################################

###############################################################################
# Check for presence of BLAS in a config context
###############################################################################

def check(context): 
	context.Message('Checking for CBLAS... ')
	if context.env['cblas'] == 'none':
		context.Result(0)	
		return 0
	ret = context.TryLink("""
#include "../include/helpers/cblas.h"

int main(int argc, char ** argv) {
	double * vecA, * vecB;
	int n;
	cblas_ddot(n, vecA, 1,vecB, 1);
	return 0;
}
""", '.c')
	context.Result(ret)	
	return ret

def make_options (opts):
	opts.AddVariables(
		('cblas', 'Which version of CBLAS to use. Allowed values: none|blas|atlas|openblas|accelerate (MacOS X only)', 'none'),
	)

###############################################################################
# Add TBB to an enviroment
###############################################################################

def generate (root):
	cblas = root['cblas']
	
	if cblas == 'blas':
		root.Append(LIBS='blas')
	elif cblas == 'atlas':
		root.Append(LIBS=[ 'cblas', 'atlas' ])
	elif cblas == 'openblas':
		root.Append(LIBS=[ 'openblas' ])
	elif cblas == 'accelerate':
		root.Prepend(LINKFLAGS = '-framework Accelerate')
