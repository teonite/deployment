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

import config

env.host = 'localhost'

def _pretty_print(str):
	print('[%s] INFO: %s' % (env.host, str))

def _prefix():
	return 'source %s' % os.path.join('~', config.ENV_DIR, 'bin/activate')

def src_clone(dir='', branch = ''):
	_pretty_print('Repository clone start')

	if len(dir) == 0:
		_pretty_print('Directory not selected, assuming current one.')
		dir = os.getcwd()

	try:
		repo = Repo(dir)
		_pretty_print('Repository found.')
	except InvalidGitRepositoryError: #Repo doesn't exists
		_pretty_print('Repository not found. Creating new one, using GIT_REPO from config.')
		repo = Repo.clone_from(config.GIT_REPO, dir)
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

	run('cp -Rfv %s %s' % (os.path.join(src_dir, "*"), dst_dir))
	run('rm previous')
	run('mv current previous')
	run('ln -s %s current' % src_dir)
	_pretty_print("Remote deployment finished")
	pass

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
	src_clone()
	src_prepare()
	src_remote_extract()
	src_remote_deploy()
	_pretty_print("Deployment finished.")

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

def list_dir(dir_=None):
	"""returns a list of files in a directory (dir_) as absolute paths"""
	dir_ = dir_ or env.cwd
	string_ = run("for i in %s*; do echo $i; done" % dir_)
	files = string_.replace("\r","").split("\n")
	return files

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
	mysql_db_dump()
	mysql_db_restore()
	mysql_db_clone()
	mysql_db_migrate()
