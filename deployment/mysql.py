#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

from __future__ import print_function

import sys
import os
from datetime import datetime

from fabric.context_managers import cd, hide
from fabric.operations import put
from fabric.state import env
from fabric.api import run
from fabric.contrib import files

from misc import *

def validate_config(config, section):

	pretty_print("Validating mysql config section: %s" % section, 'debug')

	if not 'mysql' in config:
		raise NotConfiguredError("MySQL section does not exists")

	if section == "server":
		if not 'server' in config['mysql']:
			raise NotConfiguredError("server section does not exists")

		if not 'host' in config['mysql']['server'] or not len(config['mysql']['server']['host']):
			raise NotConfiguredError("host not set")
		if not 'user' in config['mysql']['server'] or not len(config['mysql']['server']['user']):
			raise NotConfiguredError("user not set")
		if not 'password' in config['mysql']['server'] or not len(config['mysql']['server']['password']):
			raise NotConfiguredError("password not set")
		if not 'port' in config['mysql']['server'] or not (type(config['mysql']['server']['port']) == type(int)):
			pretty_print("port not set, using default one", "info")
			config['mysql']['server']['port'] = 3306
		if not 'database' in config['mysql']['server'] or not len(config['mysql']['server']['database']):
			raise NotConfiguredError("database not set")

	elif section == "shell":
		if not 'shell' in config['mysql']:
			raise NotConfiguredError("shell section does not exists")

		if not 'host' in config['mysql']['shell'] or not len(config['mysql']['shell']['host']):
			raise NotConfiguredError("host not set")
		if not 'user' in config['mysql']['shell'] or not len(config['mysql']['shell']['user']):
			raise NotConfiguredError("user not set")
		if not 'port' in config['mysql']['shell'] or not (type(config['mysql']['shell']['port']) == type(int)):
			pretty_print("port not set, using default one", "info")
			config['mysql']['shell']['port'] = 22
			env.port = config['mysql']['shell']['port']

		if not 'migration_dir' in config['mysql']['shell'] or not len(config['mysql']['shell']['migration_dir']):
			pretty_print("migration_dir not set, using default: ~/migrations")
			config['mysql']['shell']['migration_dir'] = "~/migrations"

		if not 'dumpfile' in config['mysql']['shell'] or not len(config['mysql']['shell']['dumpfile']):
			pretty_print("migration_dir not set, using default: dump.sql")
			config['mysql']['shell']['migration_dir'] = "dump.sql"

	pretty_print('Config is valid!', 'debug')

	return config

def _mysql_dump_remove(filename, host, host_user):
	env.host = host
	env.user = host_user
	env.host_string = "%s@%s:%s" %(env.user,env.host,env.port)

	pretty_print("[+] Starting dump remove.", 'info')

	if files.exists(filename):
		pretty_print('File %s found. Removing.' % filename)
		run('rm %s' % filename)
	else:
		raise Exception('Dump file not found.')

	pretty_print("[+] Dump remove finished.", 'info')

def mysql_dump_remove(config_f = 'config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, "shell")

	_mysql_dump_remove(config['mysql']['shell']['dumpfile'], config['mysql']['shell']['host'], config['mysql']['shell']['user'])

def	_mysql_db_dump(filename, database, dbhost, dbuser, dbpassword, host, host_user):
	env.host = host
	env.user = host_user
	env.host_string = "%s@%s:%s" %(env.user,env.host,env.port)

	pretty_print('[+] Starting MySQL dump.', 'info')

	with hide('running'):
		pretty_print('Running mysqldump.', 'info')
		run('mysqldump -u%s -p%s -h%s %s > %s' %(dbuser, dbpassword, dbhost, database, filename))
	pretty_print('[+] MySQL dump finished.', 'info')

def mysql_db_dump(config_f = 'config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, "shell")
	config = validate_config(config, "server")

	_mysql_db_dump(config['mysql']['shell']['dumpfile'], config['mysql']['server']['database'], config['mysql']['server']['host'], config['mysql']['server']['user'], config['mysql']['server']['password'], config['mysql']['shell']['host'], config['mysql']['shell']['user'])

def	_mysql_db_restore(filename, database, dbhost, dbuser, dbpassword, host, host_user):
	env.host = host
	env.user = host_user
	env.host_string = "%s@%s:%s" %(env.user,env.host,env.port)

	pretty_print('[+] Starting MySQL restore.', 'info')

#	env.use_ssh_config = True
	with hide('running'):
		pretty_print('Restoring to %s from %s' % (database, filename), 'info')
		run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, filename))
	pretty_print('[+] MySQL restore finished.', 'info')

def mysql_db_restore(config_f = 'config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, "shell")
	config = validate_config(config, "server")

	_mysql_db_restore(config['mysql']['shell']['dumpfile'], config['mysql']['server']['database'], config['mysql']['server']['host'], config['mysql']['server']['user'], config['mysql']['server']['password'], config['mysql']['shell']['host'], config['mysql']['shell']['user'])

def	_mysql_db_clone(database, dbhost, dbuser, dbpassword, host, host_user, dumpfile='temp.sql'):
	env.host = host
	env.user = host_user
	env.host_string = "%s@%s:%s" %(env.user,env.host,env.port)
	#	env.use_ssh_config = True

	pretty_print('[+] Starting MySQL clone.', 'info')

	new_database = '%s_%s' % (database, datetime.now().strftime("%Y%m%d_%H%M%S"))

	with hide('running'):
		_mysql_db_dump(dumpfile, database, dbhost, dbuser, dbpassword, host, host_user)
		pretty_print('Creating new database: %s' % new_database)
		run('mysql -u%s -p%s -h%s %s <<< %s' % (dbuser, dbpassword, dbhost, database,
											'\"CREATE DATABASE %s\"' % new_database))
		_mysql_db_restore(dumpfile, new_database, dbhost, dbuser, dbpassword, host, host_user)

	pretty_print('[+] MySQL clone finished.', 'info')

def mysql_db_clone(config_f = 'config.json', database = ''):
	config = prepare_config(config_f)
	config = validate_config(config, "shell")
	config = validate_config(config, "server")

	if not len(database):
		pretty_print("Database name not provided, assuming database from config.", "info")
		_mysql_db_clone(config['mysql']['server']['database'], config['mysql']['server']['host'], config['mysql']['server']['user'], config['mysql']['server']['password'], config['mysql']['shell']['host'], config['mysql']['shell']['user'], config['mysql']['shell']['dumpfile'])
	else:
		_mysql_db_clone(database, config['mysql']['server']['host'], config['mysql']['server']['user'], config['mysql']['server']['password'], config['mysql']['shell']['host'], config['mysql']['shell']['user'], config['mysql']['shell']['dumpfile'])

def	_mysql_db_migrate(database, dir, dbhost, dbuser, dbpassword, host, host_user, remote_dir):
	env.host = host
	env.user = host_user
	env.host_string = "%s@%s:%s" %(env.user,env.host,env.port)

	pretty_print('[+] Starting MySQL migrate', 'info')
#	env.use_ssh_config = True

	try:
		date = datetime.now().strftime("%Y%m%d_%H%M%S")
#		pretty_print("Current working directory: %s" % os.getcwd())
		f = []
		for (dirpath, dirname, filenames) in os.walk(dir):
			f.extend(filenames)
			break
		f.sort()
		pretty_print('Files: %s' % f)
		os.chdir(dir)
		remote_dir = os.path.join(remote_dir, date)
		pretty_print('Creating directory %s' % remote_dir, 'info')
		run('mkdir -p %s' % remote_dir)
		for file in f:
			pretty_print('Uploading file: %s' % file, 'info')
			put(file, remote_dir)

		with cd(remote_dir):
			for file in f:
				pretty_print('Migrating file %s' % file, 'info')
				with hide('running'):
					run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, file))
#			run('rm %s' % file)

		pretty_print('[+] MySQL migrate finished.', 'info')
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue), 'error')
		raise Exception

def mysql_db_migrate(migration_dir = None, config_f = 'config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, "shell")
	config = validate_config(config, "server")

	if not migration_dir:
		raise NotConfiguredError('Migration dir not set.')

	_mysql_db_migrate(config['mysql']['server']['database'], migration_dir, config['mysql']['server']['host'], config['mysql']['server']['user'], config['mysql']['server']['password'], config['mysql']['shell']['host'], config['mysql']['shell']['user'], config['mysql']['shell']['migration_dir'])

def	_db_migrate(config, migration_dir=None):
	pretty_print("[+] Starting database migration.", 'info')

	try:
		if not config:
			raise NotConfiguredError

		_mysql_db_clone(config['mysql']['server']['database'], config['mysql']['server']['host'], config['mysql']['server']['user'], config['mysql']['server']['password'], config['mysql']['shell']['host'], config['mysql']['shell']['user'], config['mysql']['shell']['dumpfile'])
		if migration_dir:
			pretty_print("Migration directory provided. Running.", 'info')
			_mysql_db_migrate(config['mysql']['server']['database'], migration_dir, config['mysql']['server']['host'], config['mysql']['server']['user'], config['mysql']['server']['password'], config['mysql']['shell']['host'], config['mysql']['shell']['user'], config['mysql']['shell']['migration_dir'])
		else:
			pretty_print("No migration directory, omitting.", "info")

		_mysql_dump_remove(config['mysql']['shell']['dumpfile'], config['mysql']['shell']['host'], config['mysql']['shell']['user'])

		pretty_print("[+] Database migration finished.", 'info')
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

def db_migrate(config_f = 'config.json', migration_dir = None):
	config = prepare_config(config_f)
	config = validate_config(config, "shell")
	config = validate_config(config, "server")

	_db_migrate(config, migration_dir)
