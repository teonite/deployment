#!/usr/bin/env python
from __future__ import print_function
import getopt

import os
import sys
from os.path import dirname, abspath
import shutil
import re
from datetime import datetime

sys.path.append(dirname(dirname(abspath(__file__))))

from fabric.context_managers import cd, prefix
from fabric.state import env
from fabric.api import run, put, settings
from fabric.contrib import files

from git import Repo, InvalidGitRepositoryError, GitCommandError, RemoteProgress

import logging
import graypy
import ConfigParser

#import config

env.host_string = 'localhost'
progress = RemoteProgress()
handler = graypy.GELFHandler('logs.teonite.net', 10514)

logger = logging.getLogger('init')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

class NotConfiguredError(Exception):
	pass

def _pretty_print(str, level='debug'):
	if level == 'debug':
		logger.debug('[%s] DEBUG: %s' % (env.host_string, str))
	elif level == 'info':
		logger.info('[%s] INFO: %s' % (env.host_string, str))
	elif level == 'error':
		logger.error('[%s] ERROR: %s' % (env.host_string, str))
	print ('[%s] %s: %s' % (env.host_string, level, str))

def _prefix():
	return
	#return 'source %s' % os.path.join('~', config.ENV_DIR, 'bin/activate')

def _config_section_map(Config, section):
	_pretty_print('Reading section %s' % section)
	dict1 = {}
	options = Config.options(section)
	for option in options:
		try:
			dict1[option] = Config.get(section, option)
			if dict1[option] == -1:
				_pretty_print("skip: %s" % option)
		except:
			_pretty_print("exception on %s!" % option)
			dict1[option] = None
	_pretty_print('Reading finished. Returning.')
	return dict1

def _parse_config(filename):
	_pretty_print("Parsing config file: %s" % filename, 'info')
	try:
		config = ConfigParser.ConfigParser()
		config.read(filename)
		conf = _config_section_map(config, 'Source')

	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Returning empty map. Message: %s - %s" % (exceptionType, exceptionValue))
		conf = {}

	return conf

def _validate_entry(config, entry, required=True, default=None):
	try:
		if not len(config[entry]):
			if not required:
				if not default:
					raise Exception('Default must be set if required == False')
				_pretty_print('%s not set, assuming %s' % (entry, default), 'info')
				config[entry] = default
			else:
				raise NotConfiguredError('%s not set.' % entry)
		else:
			_pretty_print('%s provided: %s' % (entry, config[entry]), 'debug')

	except:
		if not required:
			_pretty_print('%s not set, assuming %s' % (entry, default), 'info')
			config[entry] = default
		else:
			_pretty_print('%s not set. Please use correct one.' % entry, 'error')
			raise NotConfiguredError('%s not set.' % entry)

def _validate_section(config, section):
	_pretty_print("Validating config section: %s" % section, 'info')
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
#	MYSQL_MIGRATION_DIR = test
		_validate_entry(config, 'mysql_migration_dir', required=True, default=None)

	elif section == 'source':
#		GIT_REPO = gitolite@git.teonite.net:TEONITE/sample.git
		_validate_entry(config, 'git_repo', required=True, default=None)
#		BRANCH = master
		_validate_entry(config, 'branch', required=True, default=None)
#		LOCAL_DIR = test
		_validate_entry(config, 'local_dir', required=False, default=os.getcwd())
#		FILE_NAME = src.tar
		_validate_entry(config, 'file_name', required=False, default='src.tar')

	elif section == 'deployment':
#		UPLOAD_DIR = ~
		_validate_entry(config, 'upload_dir', required=False, default='')

#		EXTRACT_DIR = extract
		_validate_entry(config, 'extract_dir', required=True, default=None)

#		REMOTE_HOST = 192.168.56.101
		_validate_entry(config, 'remote_host', required=True, default=None)

#		REMOTE_USER = kmk
		_validate_entry(config, 'remote_user', required=True, default=None)

#		DEPLOY_DIR = deploy
		_validate_entry(config, 'deploy_dir', required=True, default=None)

	else:
		raise Exception('Invalid section provided!')

	return config

def list_dir(dir_=None):
	"""returns a list of files in a directory (dir_) as absolute paths"""
	#dir_ = dir_ or env.cwd
	string_ = run("for i in *; do echo $i; done")
	files = string_.replace("\r","").split("\n")
	return files

def src_clone(dir='', branch = '', repo = ''):
	_pretty_print('[+] Repository clone start: %s' % dir)

	if len(dir) == 0:
		_pretty_print('Directory not selected, assuming current one.')
		dir = os.getcwd()

	if os.path.isdir(dir):
		_pretty_print('Directory found, renaming.')
		shutil.move(dir, "%s-%s" %(dir, datetime.now().strftime("%Y%m%d-%H%M%S")))
	try:
		#repo = Repo(dir)
		_pretty_print('Clonning repo.')
		repo = Repo.clone_from(repo, dir, progress)
		_pretty_print('Repository found. Branch: %s' % repo.active_branch)
	except InvalidGitRepositoryError: #Repo doesn't exists
		_pretty_print('Repository not found. Creating new one, using %s.' % repo)
		if len(repo) == 0:
			_pretty_print('Repository not selected. Returning.')
			raise InvalidGitRepositoryError
		repo = Repo.clone_from(repo, dir, progress)
		#repo.create_remote('origin', config.GIT_REPO)

#	_pretty_print('Fetching changes.')

#	origin = repo.remotes.origin
#	origin.fetch()
#
#	if len(branch) == 0:
#		_pretty_print('Branch not supplied, assuming current one.')
#		origin.pull()
#	else:
#		_pretty_print('Pulling from \'%s\' branch' % branch)
#		origin.pull(branch)

	_pretty_print('[+] Repository clone finished')

def src_prepare(file, dir='', branch = ''):
	_pretty_print('[+] Archive prepare start. Branch: %s' % branch)

	try:
		repo = Repo(dir)
		_pretty_print('Repository found.')
	except InvalidGitRepositoryError: #Repo doesn't exists
		_pretty_print('Repository not found. Please provide correct one.')
		return

	try:
		if len(branch)==0:
			_pretty_print('Branch not selected. Archiving current one.')
			repo.archive(open("%s" % file,'w'))
		else:
			_pretty_print('Archiving branch %s' % branch)
			repo.archive(open("%s" % file,'w'), branch)

	except GitCommandError as ex:
		_pretty_print('Something went wrong. Message: %s' % ex.__str__())

	_pretty_print('[+] Archive prepare finished')

def src_upload(file, user, host, dir):
	_pretty_print("[+] Starting file upload.")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	env.use_ssh_config = True

	put(file, "%s/%s" %(dir, file))
	_pretty_print("[+] File upload finished")

def	src_remote_extract(file, file_dir, dest_dir, user, host):
	_pretty_print("[+] Starting remote extract")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)

	run('mkdir -p %s' % dest_dir)
	with cd(file_dir):
		run('tar xvf %s -C %s' % (file, dest_dir))

	_pretty_print("[+] Remote extract finished")

def	src_remote_deploy(src_dir, dst_dir, user, host):
	_pretty_print("[+] Starting remote deployment")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)

	path = env.cwd

	_pretty_print("current working dir: %s" % env.cwd)
	if not files.exists(dst_dir, verbose=True):
		run('mkdir -p %s-%s' % (dst_dir, datetime.now().strftime("%Y%m%d-%H%M%S")))

	#run('cp -Rfv %s %s' % (os.path.join(src_dir, "*"), dst_dir))
	with cd(dst_dir):
		#if files.exists(os.path.join(dst_dir, 'current'), verbose=True):
		with settings(warn_only=True):
			if not run('test -L previous').failed:
				run('rm -f previous')
			_pretty_print("current working dir: %s" % env.cwd)

			if not run('test -L current').failed:
				run('mv current previous')
		run('ln -s %s current' % os.path.join(path, src_dir))

	_pretty_print("[+] Remote deployment finished")

def	src_remote_rollback(dir, host, user):
	_pretty_print("[+] Starting remote rollback")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)

	with cd(dir):
		run('mv current current.prerollback')
		run('mv previous current')
	_pretty_print("[+] Remote rollback finished")

def deploy(config):
	_pretty_print("[+] Starting deployment.")

	try:
		if not config:
			raise NotConfiguredError

		_validate_section(config, 'source')
		_validate_section(config, 'deployment')

		src_clone(config['local_dir'], config['branch'], config['git_repo'])
		src_prepare(config['file_name'], config['local_dir'], config['branch'])
		src_upload(config['file_name'], config['remote_user'], config['remote_host'], config['upload_dir'])
		src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'], config['remote_user'], config['remote_host'])
		src_remote_deploy(config['extract_dir'], config['deploy_dir'], config['remote_user'], config['remote_host'])

		_pretty_print("[+] Deployment finished.")
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

def	mysql_db_dump(filename, database, dbhost, dbuser, dbpassword, host, host_user):
	_pretty_print('[+] Starting MySQL dump.')
	env.hosts = [host]
	env.user = host_user
	env.use_ssh_config = True

	run('mysqldump -u%s -p%s -h%s %s > %s' %(dbuser, dbpassword, dbhost, database, filename))
	_pretty_print('[+] MySQL dump finished.')

def	mysql_db_restore(filename, database, dbhost, dbuser, dbpassword, host, host_user):
	_pretty_print('[+] Starting MySQL restore.')
	env.hosts = [host]
	env.user = host_user
	env.use_ssh_config = True

	run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, filename))
	_pretty_print('[+] MySQL restore finished.')

def	mysql_db_clone(database, dbhost, dbuser, dbpassword, host, host_user):
	_pretty_print('[+] Starting MySQL clone.')

	env.host = host
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)
	env.use_ssh_config = True

	new_database = '%s_%s' % (database, datetime.now().strftime("%Y%m%d_%H%M%S"))

	mysql_db_dump('temp.sql', database, dbhost, dbuser, dbpassword, host, host_user)
	run('mysql -u%s -p%s -h%s %s <<< %s' % (dbuser, dbpassword, dbhost, database,
									 '\"CREATE DATABASE %s\"' % new_database))
	mysql_db_restore('temp.sql', new_database, dbhost, dbuser, dbpassword, host, host_user)

	_pretty_print('[+] MySQL clone finished.')

def	mysql_db_migrate(database, dir, dbhost, dbuser, dbpassword, host, host_user):
	_pretty_print('[+] Starting MySQL migrate')

	env.host = host
	env.user = host_user
	env.host_string = "%s@%s" %(host_user,host)
	env.use_ssh_config = True

	try:
		with(cd(dir)):
			for file in list_dir():
				run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, file))

		_pretty_print('[+] MySQL migrate finished.')
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))
		raise Exception

def	db_migrate(config):
	_pretty_print("[+] Starting database migration.")

	try:
		if not config:
			raise NotConfiguredError
		_validate_section(config, 'mysql')

		mysql_db_clone(config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])
		mysql_db_migrate(config['mysql_database'], config['mysql_migration_dir'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

		_pretty_print("[+] Database migration finished.")
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

def usage():
	_pretty_print('Parameters:')
	_pretty_print(' -c, --config <filename> - if not selected, config.ini is selected')
	_pretty_print('Usage:')
	_pretty_print(' - deploy - deploys new version')
	_pretty_print(' - db_migrate - migrate database to new version')
	_pretty_print(' - src_clone - clone repo to local folder')
	_pretty_print(' - src_prepare - archive repo to file')
	_pretty_print(' - src_upload - upload packed file to remote host')
	_pretty_print(' - src_remote_extract - extract uploaded file')
	_pretty_print(' - src_remote_deploy - deploys new version')
	_pretty_print(' - mysql_db_clone - clone db: <db_name> -> <db_name>_<current_date>_<current_time>')
	_pretty_print(' - mysql_db_migrate - runs .sql files from selected folder')
	_pretty_print(' - mysql_db_dump - dump database to selected file')
	_pretty_print(' - mysql_db_restore - restore database from file')

if __name__ == "__main__":
	if len(sys.argv) == 1:
		usage()
		sys.exit()

	try:
		opts, args = getopt.getopt(sys.argv[2:], "c:", ["config="])
	except getopt.GetoptError as err:
		# print help information and exit:
		_pretty_print(str(err)) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	config_f = None
	for o, a in opts:
		if o == "-c" or o == "--config":
			config_f = a
		else:
			_pretty_print("unhandled option")

	config = None
	try:
		if not config_f:
			config = _parse_config("config.ini")
		else:
			config = _parse_config(config_f)

		if not config['project_name']:
			raise Exception('Project name not set.')

		logger = logging.getLogger(config['project_name'])
		logger.setLevel(logging.DEBUG)
		logger.addHandler(handler)

	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

	try:
		s = sys.argv[1]
		if s == 'deploy':
			deploy(config)
		elif s == 'db_migrate':
			db_migrate(config)
		elif s == 'src_clone':
			_validate_section(config, 'source')
			src_clone(config['local_dir'], config['branch'], config['git_repo'])
		elif s == 'src_prepare':
			_validate_section(config, 'source')
			src_prepare(config['file_name'], config['local_dir'], config['branch'])
		elif s == 'src_upload':
			_validate_section(config, 'source')
			_validate_section(config, 'deployment')
			src_upload(config['file_name'], config['remote_user'], config['remote_host'], config['upload_dir'])
		elif s == 'src_remote_extract':
			_validate_section(config, 'source')
			_validate_section(config, 'deployment')
			src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'], config['remote_user'], config['remote_host'])
		elif s == 'src_remote_deploy':
			_validate_section(config, 'deployment')
			src_remote_deploy(config['extract_dir'], config['deploy_dir'], config['remote_user'], config['remote_host'])
		elif s == 'mysql_db_clone':
			_validate_section(config, 'mysql')
			mysql_db_clone(config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])
		elif s == 'mysql_db_migrate':
			_validate_section(config, 'mysql')
			mysql_db_migrate(config['mysql_database'], config['mysql_migration_dir'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])
		elif s == 'mysql_db_dump':
			_validate_section(config, 'mysql')
			mysql_db_dump(config['mysql_dumpfile'], config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])
		elif s == 'mysql_db_restore':
			_validate_section(config, 'mysql')
			mysql_db_restore(config['mysql_dumpfile'], config['mysql_database'], config['mysql_host'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])
		else:
			usage()
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))
