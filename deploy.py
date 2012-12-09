from __future__ import print_function

import os
import sys
from os.path import dirname, abspath
import re
from datetime import datetime

sys.path.append(dirname(dirname(abspath(__file__))))

from fabric.context_managers import cd, prefix
from fabric.state import env
from fabric.api import run, put
from fabric.contrib import files

from git import Repo, InvalidGitRepositoryError, GitCommandError

import ConfigParser

#import config

env.host = 'localhost'

def _pretty_print(str):
	print('[%s] INFO: %s' % (env.host, str))

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
	_pretty_print("Parsing config file: %s" % filename)
	try:
		config = ConfigParser.ConfigParser()
		config.read(filename)
		conf = _config_section_map(config, 'General')
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Returning empty map. Message: %s - %s" % (exceptionType, exceptionValue))
		conf = {}

	return conf

def list_dir(dir_=None):
	"""returns a list of files in a directory (dir_) as absolute paths"""
	dir_ = dir_ or env.cwd
	string_ = run("for i in %s*; do echo $i; done" % dir_)
	files = string_.replace("\r","").split("\n")
	return files

def src_clone(dir='', branch = '', repo = ''):
	_pretty_print('Repository clone start')

	if len(dir) == 0:
		_pretty_print('Directory not selected, assuming current one.')
		dir = os.getcwd()

	try:
		repo = Repo(dir)
		_pretty_print('Repository found.')
	except InvalidGitRepositoryError: #Repo doesn't exists
		_pretty_print('Repository not found. Creating new one, using provided git url.')
		if len(repo) == 0:
			_pretty_print('Repository not selected. Returning.')
			raise InvalidGitRepositoryError
		repo = Repo.clone_from(repo, dir)
		#repo.create_remote('origin', config.GIT_REPO)

	_pretty_print('Fetching changes.')

	origin = repo.remotes.origin
	origin.fetch()

	if len(branch) == 0:
		_pretty_print('Branch not supplied, assuming current one.')
		origin.pull()
	else:
		_pretty_print('Pulling from \'%s\' branch' % branch)
		origin.pull(branch)

	_pretty_print('Repository clone finished')

def src_prepare(file, dir='', branch = ''):
	_pretty_print('Archive prepare start')

	try:
		repo = Repo(dir)
		_pretty_print('Repository found.')
	except InvalidGitRepositoryError: #Repo doesn't exists
		_pretty_print('Repository not found. Please provide correct one.')
		return

	try:
		if len(branch) is not 0:
			_pretty_print('Branch not selected. Archiving current one.')
			repo.archive(open("%s.tar" % file,'w'))
		else:
			_pretty_print('Archiving branch %s' % branch)
			repo.archive(open("%s.tar" % file,'w'), branch)

	except GitCommandError as ex:
		_pretty_print('Something went wrong. Message: %s' % ex.__str__())

	_pretty_print('Archive prepare finished')

def src_upload(file, user, host, dir):
	_pretty_print("Starting file upload.")
	put(file, '%s@%s:%s' % (user, host, dir))
	_pretty_print("File upload finished")

def	src_remote_extract(file, file_dir, dest_dir, user, host):
	_pretty_print("Starting remote extract")

	env.hosts = [host]
	env.user = user
	env.use_ssh_config = True

	with cd(file_dir):
		run('tar xvf %s -C %s' % (file, dest_dir))

	_pretty_print("Remote extract finished")

def	src_remote_deploy(src_dir, dst_dir, user, host):
	_pretty_print("Starting remote deployment")

	env.hosts = [host]
	env.user = user
	env.use_ssh_config = True

	#run('cp -Rfv %s %s' % (os.path.join(src_dir, "*"), dst_dir))
	run('rm previous')
	run('mv current previous')
	run('ln -s %s current' % src_dir)
	_pretty_print("Remote deployment finished")

def	src_remote_rollback(dir, host, user):
	_pretty_print("Starting remote rollback")

	env.hosts = [host]
	env.user = user
	env.use_ssh_config = True
	with cd(dir):
		run('mv current current.prerollback')
		run('mv previous current')
	_pretty_print("Remote rollback finished")

def deploy():
	_pretty_print("Starting deployment.")

	try:
		config = _parse_config("config.ini")

		src_clone(config['local_dir'], config['branch'], config['git_repo'])
		src_prepare(config['file_name'], config['local_dir'], config['branch'])
		src_upload(config['file_name'], config['remote_user'], config['remote_host'], config['upload_dir'])
		src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'])
		src_remote_deploy(config['extract_dir'], config['deploy_dir'], config['remote_user'], config['remote_host'])

		_pretty_print("Deployment finished.")
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

def	mysql_db_dump(filename, database, dbuser, dbpassword, host, host_user):
	_pretty_print('Starting MySQL dump.')
	env.hosts = [host]
	env.user = host_user
	env.use_ssh_config = True

	run('mysqldump -u%s -p%s %s > %s' %(dbuser, dbpassword, database, filename))
	_pretty_print('MySQL dump finished.')

def	mysql_db_restore(filename, database, dbuser, dbpassword, host, host_user):
	_pretty_print('Starting MySQL restore.')
	env.hosts = [host]
	env.user = host_user
	env.use_ssh_config = True

	run('mysql -u%s -p%s %s < %s' % (dbuser, dbpassword, database, filename))
	_pretty_print('MySQL restore finished.')

def	mysql_db_clone(database, dbuser, dbpassword, host, host_user):
	_pretty_print('Starting MySQL clone.')

	env.hosts = [host]
	env.user = host_user
	env.use_ssh_config = True

	new_database = '%s-%s' % (database, datetime.now().strftime("%Y%m%d"))

	mysql_db_dump('temp.sql', database, dbuser, dbpassword, host, host_user)
	run('mysql -u%s -p%s %s < %s' % (dbuser, dbpassword, database,
									 'CREATE DATABASE %s' % new_database))
	mysql_db_restore('temp.sql', new_database, dbuser, dbpassword, host, host_user)

	_pretty_print('MySQL clone finished.')

def	mysql_db_migrate(database, dir, dbuser, dbpassword, host, host_user):
	_pretty_print('Starting MySQL migrate')
	env.hosts = [host]
	env.user = host_user
	env.use_ssh_config = True
	with(cd(dir)):
		for file in list_dir():
			run('mysql -u%s -p%s %s < %s' % (dbuser, dbpassword, database, file))

	_pretty_print('MySQL migrate finished.')

def	db_migrate():
	_pretty_print("Starting database migration.")

	try:
		config = _parse_config("config.ini")

		mysql_db_clone(config['mysql_database'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])
		mysql_db_migrate(config['mysql_database'], config['mysql_migration_dir'], config['mysql_user'], config['mysql_password'], config['mysql_shell_host'], config['mysql_shell_user'])

		_pretty_print("Database migration finished.")
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

if __name__ == "__main__":
	if not len(sys.argv[1]):
		usage()
		sys.exit()

	s = sys.argv[1]
	if s == 'install':
		install()
	elif s == 'deploy':
		deploy()
	elif s == 'upgrade':
		upgrade()
	elif s == 'dbsync':
		dbsync()
	else:
		usage()
