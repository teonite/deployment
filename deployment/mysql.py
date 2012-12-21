#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

from __future__ import print_function

import sys
from datetime import datetime

from fabric.context_managers import cd, hide
from fabric.operations import put
from fabric.state import env
from fabric.api import run


from misc import *

def	_mysql_db_dump(filename, database, dbhost, dbuser, dbpassword, host, host_user):
	env.hosts = [host]
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)

	pretty_print('[+] Starting MySQL dump.', 'info')

	with hide('running'):
		pretty_print('Running mysqldump.', 'info')
		run('mysqldump -u%s -p%s -h%s %s > %s' %(dbuser, dbpassword, dbhost, database, filename))
	pretty_print('[+] MySQL dump finished.', 'info')

def mysql_db_dump(config_f = 'config.ini'):
	config = prepare_config(config_f)
	config_validate_section(config, 'mysql')
	_mysql_db_dump(config['mysql_dumpfile'], config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

def	_mysql_db_restore(filename, database, dbhost, dbuser, dbpassword, host, host_user):
	env.hosts = [host]
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)

	pretty_print('[+] Starting MySQL restore.', 'info')

#	env.use_ssh_config = True
	with hide('running'):
		pretty_print('Restoring to %s from %s' % (database, filename), 'info')
		run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, filename))
	pretty_print('[+] MySQL restore finished.', 'info')

def mysql_db_restore(config_f = 'config.ini'):
	config = prepare_config(config_f)

	config_validate_section(config, 'mysql')
	_mysql_db_restore(config['mysql_dumpfile'], config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

def	_mysql_db_clone(database, dbhost, dbuser, dbpassword, host, host_user, dumpfile='temp.sql'):
	env.host = host
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)
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

def mysql_db_clone(config_f = 'config.ini'):
	config = prepare_config(config_f)

	config_validate_section(config, 'mysql')
	_mysql_db_clone(config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'], config['mysql_dumpfile'])

def	_mysql_db_migrate(database, dir, dbhost, dbuser, dbpassword, host, host_user):
	env.host = host
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)

	pretty_print('[+] Starting MySQL migrate', 'info')
#	env.use_ssh_config = True

	try:
#		pretty_print("Current working directory: %s" % os.getcwd())
		f = []
		for (dirpath, dirname, filenames) in os.walk(dir):
			f.extend(filenames)
			break
		f.sort()
		pretty_print('Files: %s' % f)
		os.chdir(dir)
		for file in f:
			pretty_print('Migrating file %s' % file, 'info')
			put(file)
			with hide('running'):
				run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, file))
			run('rm %s' % file)

		pretty_print('[+] MySQL migrate finished.', 'info')
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))
		raise Exception

def mysql_db_migrate(migration_dir = None, config_f = 'config.ini'):
	config = prepare_config(config_f)
	if not migration_dir:
		raise NotConfiguredError('Migration dir not set.')

	config_validate_section(config, 'mysql')
	_mysql_db_migrate(config['mysql_database'], migration_dir, config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

def	_db_migrate(config, migration_dir=None):
	pretty_print("[+] Starting database migration.", 'info')

	try:
		if not config:
			raise NotConfiguredError
		config_validate_section(config, 'mysql')

		_mysql_db_clone(config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])
		if migration_dir:
			pretty_print("Migration directory provided. Running.", 'info')
			_mysql_db_migrate(config['mysql_database'], migration_dir, config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])
		else:
			pretty_print("No migration directory, omitting.", "info")

		pretty_print("[+] Database migration finished.", 'info')
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

def db_migrate(config_f = 'config.ini', migration_dir = None):
	config = prepare_config(config_f)
	_db_migrate(config, migration_dir)
