
import platform

###############################################################################
# Automatic configuration code
###############################################################################

"""Autoconfig function

@param root an environment to use
@param crunner a config runner function (def crunner (conf, autohdr) )
@param customtests a set of custom tests to use for the config enviroment
"""

def AutoConfig (root, crunner,customtests = {}):	
	platform_name = platform.uname()[0]
	subarch = platform.uname()[4]

	conf = root.Configure(custom_tests = customtests )
	
	autohdr = open("src/autoconfig.h", 'w')

	# configure environment
	print "Performing autoconfiguration for " + platform_name + "/" + subarch
	autohdr.write("""
/**
 * @file autoconfig.h
 * @brief Automatically generated configuration file.
 */

/*
 * This file is generated automatically and will be overwritten whenever BSPonMPI is built.
 */ 
#ifndef __AUTOCONFIG_H__
#define __AUTOCONFIG_H__

""")
	
	crunner(conf, autohdr)

	autohdr.write("""
#endif /* __AUTOCONFIG_H__ */
""")


	root = conf.Finish()
	autohdr.close()

