###############################################################################
# Copyright (C) 2007   Peter Krusche, The University of Warwick         
# pkrusche@gmail.com
###############################################################################

from SCons.Defaults import *
import xscons

root = xscons.make_root_env(['mex']);

Export('root')

###############################################################################
# get SConscripts
###############################################################################

SConscript('src/SConscript')
SConscript('tests/SConscript')
