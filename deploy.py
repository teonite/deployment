from __future__ import print_function

import os
import sys
from os.path import dirname, abspath
import re

sys.path.append(dirname(dirname(abspath(__file__))))

from fabric.context_managers import cd, prefix
from fabric.state import env
from fabric.api import run
from fabric.contrib import files

from git import Repo, InvalidGitRepositoryError, GitCommandError

import config

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

def src_upload(file, host):
	pass

def	src_remote_extract(file, host):
	pass

def	src_remote_deploy(src_dir, dst_dir):
	pass

def	src_remote_rollback(dir):
	pass

def deploy():
	pass
def	mysql_db_dump():
	pass
def	mysql_db_restore():
	pass
def	mysql_db_clone():
	pass
def	mysql_db_migrate():
	pass
def	db_migrate():
	pass