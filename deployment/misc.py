#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#
from __future__ import print_function

import os
import sys

from fabric.state import env
from fabric.api import run

import logging, logging.config
import ConfigParser
import traceback

_log = None

def _setupLogging():
	"""
	Setup logging
	"""
	config_file = None

	if os.environ['VIRTUAL_ENV']:
		config_file = os.path.join(os.environ['VIRTUAL_ENV'], 'config/logger.conf')

	if os.path.exists('config/logger.conf'):
		config_file = 'config/logger.conf'

	if not config_file:
		print ('FATAL: Cannot find logging configuration file')
		sys.exit()

	logging.config.fileConfig(config_file)
	_log = logging

def getLogger():
	"Get configured logger"

	if _log is None:
		_setupLogging()

	return logging.getLogger('deployment')

log = getLogger()

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

def _config_section_map(Config, section):
	pretty_print('Reading section %s' % section)
	dict1 = {}
	options = Config.options(section)
	for option in options:
		try:
			dict1[option] = Config.get(section, option)
			if dict1[option] == -1:
				pretty_print("skip: %s" % option)
		except:
			pretty_print("exception on %s!" % option)
			dict1[option] = None
	pretty_print('Reading finished. Returning.')
	return dict1

def _parse_config(filename, section):
	pretty_print("Parsing config file: %s" % filename, 'info')
	try:
		config = ConfigParser.ConfigParser()
		config.read(filename)
		conf = _config_section_map(config, section)

	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Returning empty map. Message: %s - %s" % (exceptionType, exceptionValue))
		conf = {}

	return conf

def validate_entry(config, entry, required=True, default=None):
	try:
		if not len(config[entry]):
			if not required:
				if not default:
					raise Exception('Default must be set if required == False')
				pretty_print('%s not set, assuming %s' % (entry, default), 'info')
				config[entry] = default
			else:
				raise NotConfiguredError('%s not set.' % entry)
		else:
			pretty_print('%s provided: %s' % (entry, config[entry]), 'debug')

	except:
		if not required:
			pretty_print('%s not set, assuming %s' % (entry, default), 'info')
			config[entry] = default
		else:
			pretty_print('%s not set. Please use correct one.' % entry, 'error')
			raise NotConfiguredError('%s not set.' % entry)

def list_dir(dir_=None):
	"""returns a list of files in a directory (dir_) as absolute paths"""
	#dir_ = dir_ or env.cwd
	string_ = run("for i in *; do echo $i; done")
	files = string_.replace("\r","").split("\n")
	return files

def prepare_config(config_f = None, section = None):
	config = None
	try:
		if not config_f:
			config = _parse_config("config.ini", section)
		else:
			config = _parse_config(config_f, section)

	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))
	return config
