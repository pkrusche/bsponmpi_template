import platform

###############################################################################
# Make add options to an environment to use MSVC
###############################################################################

#
# Required options in root env:
#   mode		: 'debug' or 'release
#   debuginfo	: true or false  to include debug info also in release version
#   profile  	: true or false  to enable/disable gprof support
#

def generate (root):
    mode      = root['mode']
    debuginfo = root['debuginfo']
    profile   = root['profile']

    if mode == 'debug' or profile:
        debuginfo = True

    root.Append(
	    CCFLAGS= "/EHsc /nologo /W3 /wd4099 /D_CRT_SECURE_NO_DEPRECATE /WL /Zi",
	    LINKFLAGS = "/LARGEADDRESSAWARE:NO",
    )

    if debuginfo:
        root.Append(
		    CCFLAGS = '',
		    LINKFLAGS = '/DEBUG',
	    )

    if mode == 'debug':
        root.Append(
		    CCFLAGS = '/MDd /RTC1 /RTCu /RTCs /Od',
	    )

    if mode == 'release':
        root.Append( 
		    CCFLAGS='/MD /Ox',
	    )

#    subarch   = platform.uname()[4]
#    if subarch == 'AMD64':
#        root.Append(
#		    ARFLAGS = '/MACHINE:X64',
#		    LINKFLAGS = '/MACHINE:X64',
#	    )
#    else:
#       root.Append(
#	    ARFLAGS = '/MACHINE:X86',
#	    LINKFLAGS = '/MACHINE:X86',
#	    )
