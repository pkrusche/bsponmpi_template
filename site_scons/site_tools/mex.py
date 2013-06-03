# mex.py:  Matlab extension builder

# Based on http://scons.org/wiki/MexBuilder by
# Joe VanAndel, vanandel@ucar.edu, 2010/1/15


import os
import SCons
import sys, traceback

from SCons.Builder import Builder
from subprocess import Popen,PIPE

def findMatlab(env, tool='mex'):
    if env.get('MATLAB_PATH'):
        return os.path.join(env['MATLAB_PATH'], tool)

    extra_paths = [ '/usr/bin', '/usr/local/bin' ]

    if env.has_key('OPT_PREFIX'):
        extra_paths.append("%s/bin" % env['OPT_PREFIX'])

    return env.WhereIs(tool, extra_paths)

def getMexPath(env):
    mex = findMatlab(env)
    if not mex:
        mex = "mex"
    return mex

def generate(env):
    bld = Builder(action = '$MEX $SOURCE -o $TARGET $MATLAB_MEX_EXTRA $_CCCOMCOM $_LIBDIRFLAGS $_LIBFLAGS $LINKFLAGS ')
    env['BUILDERS']['MEX'] = bld
    env['MEX'] = findMatlab(env, 'mex')

    mexext = findMatlab(env, 'mexext')
    if not mexext:
        mexext = 'mexext'

    try:
        cmd = [ mexext ]
        # invoke matlab

        p1 = Popen(cmd, stdout=PIPE)
        env['MEX_EXT']  = p1.communicate()[0][:-1]

        print "Matlab found, using mex extension: %s" % env['MEX_EXT']

    except Exception, e:
        if env.get('MATLAB_PATH'):
            print "Could not automatically determine mex extension. " + str(e)
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        else:
            print "MEX wasn't found [set MATLAB_PATH to enable]."
        env['MEX_EXT']  = 'mex'


def exists(env):
    if not findMatlab(env, 'mex'):
        SCons.Warnings.warn(SCons.Warning, "Could not find mex program.")
        return False
    return True