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

	if os.path.exists('logger.conf'):
		config_file = 'logger.conf'

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

def _parse_config(filename):
	pretty_print("Parsing config file: %s" % filename, 'info')
	try:
		config = ConfigParser.ConfigParser()
		config.read(filename)
		conf = _config_section_map(config, 'General')

	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Returning empty map. Message: %s - %s" % (exceptionType, exceptionValue))
		conf = {}

	return conf

def _validate_entry(config, entry, required=True, default=None):
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

def config_validate_section(config, section):
	pretty_print("Validating config section: %s" % section, 'info')
	if section == 'mysql':
	#	MYSQL_DUMPFILE = temp.sql
		_validate_entry(config, 'mysql_dumpfile', required=False, default='dump.sql')
		#	MYSQL_SHELL_USER = kmk
		_validate_entry(config, 'mysql_shell_user', required=True, default=None)
		#	MYSQL_SHELL_HOST = 192.168.56.101
		_validate_entry(config, 'mysql_shell_host', required=True, default=None)
		#	MYSQL_HOST = localhost
		_validate_entry(config, 'mysql_host', required=False, default='localhost')

		#	MYSQL_USER = root
		_validate_entry(config, 'mysql_user', required=True, default=None)
		#	MYSQL_PASSWORD = test
		_validate_entry(config, 'mysql_password', required=True, default=None)
		#	MYSQL_DATABASE = base
		_validate_entry(config, 'mysql_database', required=True, default=None)
		#	MYSQL_REMOTE_DIR = test
		_validate_entry(config, 'mysql_remote_dir', required=True, default=None)

	elif section == 'source':
	#		GIT_REPO = gitolite@git.teonite.net:TEONITE/sample.git
		_validate_entry(config, 'git_repo', required=True, default=None)
		#		BRANCH = master
		_validate_entry(config, 'branch', required=True, default=None)
		#		LOCAL_DIR = test
		_validate_entry(config, 'local_dir', required=False, default=os.getcwd())
		config['local_dir'] = os.path.expanduser(config['local_dir'])
		#		FILE_NAME = src.tar
		_validate_entry(config, 'file_name', required=False, default='src.tar')
		config['file_name'] = os.path.expanduser(config['file_name'])
	elif section == 'deployment':
	#		UPLOAD_DIR = ~
		_validate_entry(config, 'upload_dir', required=False, default='')

		#		EXTRACT_DIR = extract
#		_validate_entry(config, 'extract_dir', required=True, default=None)

		#		REMOTE_HOST = 192.168.56.101
		_validate_entry(config, 'remote_host', required=True, default=None)

		#		REMOTE_USER = kmk
		_validate_entry(config, 'remote_user', required=True, default=None)

		#		DEPLOY_DIR = deploy
		_validate_entry(config, 'deploy_dir', required=True, default=None)

		#		CONFIG_TO_COPY = [{"dest": "logger.conf", "src": "logger.conf.tpl"}]
		_validate_entry(config, 'config_to_copy', required=True, default=None)

		# UPLOAD_CLEAN = False
		_validate_entry(config, 'upload_clean', required=False, default='False')

		#		POST_DEPLOY = echo "DONE"
		_validate_entry(config, 'post_deploy', required=False, default='')

		#		PRE_DEPLOY = echo "START"
		_validate_entry(config, 'pre_deploy', required=False, default='')

	else:
		raise Exception('Invalid section provided!')

	pretty_print('Config section %s is valid!' % section)
	return config

def list_dir(dir_=None):
	"""returns a list of files in a directory (dir_) as absolute paths"""
	#dir_ = dir_ or env.cwd
	string_ = run("for i in *; do echo $i; done")
	files = string_.replace("\r","").split("\n")
	return files

def prepare_config(config_f = None):
	config = None
	try:
		if not config_f:
			config = _parse_config("config.ini")
		else:
			config = _parse_config(config_f)

	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))
	return config
