from __future__ import print_function

import sys
from datetime import datetime

from fabric.context_managers import cd
from fabric.state import env
from fabric.api import run


from misc import *

def	_mysql_db_dump(filename, database, dbhost, dbuser, dbpassword, host, host_user):
	_pretty_print('[+] Starting MySQL dump.')
	env.hosts = [host]
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)
	#	env.use_ssh_config = True

	run('mysqldump -u%s -p%s -h%s %s > %s' %(dbuser, dbpassword, dbhost, database, filename))
	_pretty_print('[+] MySQL dump finished.')

def mysql_db_dump(config_f = 'config.ini'):
	config = _prepare_config(config_f)
	_validate_section(config, 'mysql')
	_mysql_db_dump(config['mysql_dumpfile'], config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

def	_mysql_db_restore(filename, database, dbhost, dbuser, dbpassword, host, host_user):
	_pretty_print('[+] Starting MySQL restore.')
	env.hosts = [host]
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)
	#	env.use_ssh_config = True

	run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, filename))
	_pretty_print('[+] MySQL restore finished.')

def mysql_db_restore(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'mysql')
	_mysql_db_restore(config['mysql_dumpfile'], config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

def	_mysql_db_clone(database, dbhost, dbuser, dbpassword, host, host_user):
	_pretty_print('[+] Starting MySQL clone.')

	env.host = host
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)
	#	env.use_ssh_config = True

	new_database = '%s_%s' % (database, datetime.now().strftime("%Y%m%d_%H%M%S"))

	_mysql_db_dump('temp.sql', database, dbhost, dbuser, dbpassword, host, host_user)
	run('mysql -u%s -p%s -h%s %s <<< %s' % (dbuser, dbpassword, dbhost, database,
											'\"CREATE DATABASE %s\"' % new_database))
	_mysql_db_restore('temp.sql', new_database, dbhost, dbuser, dbpassword, host, host_user)

	_pretty_print('[+] MySQL clone finished.')

def mysql_db_clone(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'mysql')
	_mysql_db_clone(config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

def	_mysql_db_migrate(database, dir, dbhost, dbuser, dbpassword, host, host_user):
	_pretty_print('[+] Starting MySQL migrate')

	env.host = host
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)
	#	env.use_ssh_config = True

	try:
		with(cd(dir)):
			for file in list_dir():
				run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, file))

		_pretty_print('[+] MySQL migrate finished.')
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))
		raise Exception

def mysql_db_migrate(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'mysql')
	_mysql_db_migrate(config['mysql_database'], config['mysql_migration_dir'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

def	_db_migrate(config):
	_pretty_print("[+] Starting database migration.")

	try:
		if not config:
			raise NotConfiguredError
		_validate_section(config, 'mysql')

		_mysql_db_clone(config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])
		_mysql_db_migrate(config['mysql_database'], config['mysql_migration_dir'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

		_pretty_print("[+] Database migration finished.")
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

def db_migrate(config_f = 'config.ini'):
	config = None
	try:
		if not config_f:
			config = _parse_config("config.ini")
		else:
			config = _parse_config(config_f)

	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

	_db_migrate(config)
