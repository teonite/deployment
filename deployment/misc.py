#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#
from __future__ import print_function

import sys

from fabric.state import env
from fabric.api import run

import logging, logging.config
import json
import traceback

version = "1.1.0"

_log = None
log = None

def _setupLogging(config):
	"""
	Setup logging
	"""
	global _log
	logging.config.dictConfig(config)
	_log = logging

def getLogger(config):
	"Get configured logger"

	if _log is None:
		if not 'logger' in config:
			raise NotConfiguredError("Logger section does not exists")

		_setupLogging(config['logger'])

	return logging.getLogger('deployment')

def prepare_logger(config_f):
	global log
	config = prepare_config(config_f)
	log = getLogger(config)

def logException(ex):
	log.debug("Error while saving form..")
	exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
	log.error("exception caught while saving form, here's the trace: '%s'",
		repr(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback))
	)
#import config

class NotConfiguredError(Exception):
	pass

def pretty_print(str, level='debug'):
	if level == 'debug':
		log.debug('[%s] DEBUG: %s' % (env.host_string, str))
	elif level == 'info':
		log.info('[%s] INFO: %s' % (env.host_string, str))
	elif level == 'error':
		log.error('[%s] ERROR: %s' % (env.host_string, str))
	#print ('[%s] %s: %s' % (env.host_string, level, str))

def _prefix():
	return
#return 'source %s' % os.path.join('~', config.ENV_DIR, 'bin/activate')

def _parse_config(filename, section=None):
	#pretty_print("Parsing config file: %s" % filename, 'debug')
	try:
		f = open(filename, 'r')
		conf = json.load(f)
		# pretty_print(conf[section], 'debug')

		return conf

	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Returning empty map. Message: %s - %s" % (exceptionType, exceptionValue))
		return {}

def prepare_config(config_f = None, section = None):
	config = None
	try:
		if not config_f:
			config = _parse_config("config.json")
		else:
			config = _parse_config(config_f)

	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

	return config

def list_dir(dir_=None):
	"""returns a list of files in a directory (dir_) as absolute paths"""
	#dir_ = dir_ or env.cwd
	string_ = run("for i in *; do echo $i; done")
	files = string_.replace("\r","").split("\n")
	return files