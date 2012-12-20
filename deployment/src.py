from __future__ import print_function

import os
import sys
import shutil
from datetime import datetime

from fabric.context_managers import cd
from fabric.state import env
from fabric.api import run, put, settings
from fabric.contrib import files

from git import Repo, InvalidGitRepositoryError, GitCommandError, RemoteProgress
import json

from misc import *

progress = RemoteProgress()

def _src_clone(dir='', branch = '', repo = ''):
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

def src_clone(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'source')
	_src_clone(config['local_dir'], config['branch'], config['git_repo'])

def _src_prepare(file, dir='', branch = ''):
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

def src_prepare(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'source')
	_src_prepare(config['file_name'], config['local_dir'], config['branch'])

def _src_upload(file, user, host, dir):
	_pretty_print("[+] Starting file upload.")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	env.use_ssh_config = True

	put(file, "%s/%s" %(dir, file))
	_pretty_print("[+] File upload finished")

def src_upload(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'source')
	_validate_section(config, 'deployment')
	_src_upload(config['file_name'], config['remote_user'], config['remote_host'], config['upload_dir'])

def _src_remote_test (user, host):
	_pretty_print("[+] Starting remote test", "info")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	run('exit 0')

def src_remote_test(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'deployment')
	_src_remote_test(config['remote_user'], config['remote_host'])

def	_src_remote_extract(file, file_dir, dest_dir, user, host):
	_pretty_print("[+] Starting remote extract")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	date = datetime.now().strftime("%Y%m%d-%H%M%S")

	if not files.exists(dest_dir, verbose=True):
		run('mkdir -p %s' % dest_dir)
	else:
		run('mv %s %s-%s' % (dest_dir, dest_dir, date))
		run('mkdir -p %s' % dest_dir)

	with cd(file_dir):
		run('tar xvf %s -C %s' % (file, dest_dir))

	_pretty_print("[+] Remote extract finished")

def src_remote_extract(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'source')
	_validate_section(config, 'deployment')
	_src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'], config['remote_user'], config['remote_host'])

def _src_remote_config(json_string, src_dir, dst_dir, user, host):
	_pretty_print("[+] Starting remote config copy", 'info')

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	filelist = json.loads(json_string)
	if not files.exists(dst_dir):
		_pretty_print('%s does not exists. Creating.' % dst_dir, 'info')
		run('mkdir -p %s' %dst_dir)

	for object in filelist:
		if files.exists(os.path.join(dst_dir, 'current', object['src']), verbose=True):
			_pretty_print('Copying file %s' %object, 'info')
			run('cp -rf %s %s' % (os.path.join(dst_dir, 'current', object['src']), os.path.join(src_dir, object['dest'])))
		else:
			_pretty_print('File does not exists: %s, ommiting' % os.path.join(dst_dir, 'current', object['src']), 'error')

def src_remote_config(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'source')
	_validate_section(config, 'deployment')
	_src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'], config['remote_user'], config['remote_host'])

def	_src_remote_deploy(src_dir, dst_dir, user, host):
	_pretty_print("[+] Starting remote deployment")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	path = env.cwd

	deploy_dir = datetime.now().strftime("%Y%m%d-%H%M%S")
	_pretty_print("current working dir: %s" % env.cwd)
	if not files.exists(dst_dir, verbose=True):
		run('mkdir -p %s' % dst_dir)

	#run('cp -Rfv %s %s' % (os.path.join(src_dir, "*"), dst_dir))
	with cd(dst_dir):
		if not files.exists(deploy_dir, verbose=True):
			run('mkdir -p %s' % deploy_dir)
		run('cp -Rfv %s %s' % (os.path.join('..', src_dir, "*"), deploy_dir))
		#if files.exists(os.path.join(dst_dir, 'current'), verbose=True):
		with settings(warn_only=True):
			if not run('test -L previous').failed:
				run('rm -f previous')
			_pretty_print("current working dir: %s" % env.cwd)

			if not run('test -L current').failed:
				run('mv current previous')
		run('ln -s %s current' % deploy_dir)

	_pretty_print("[+] Remote deployment finished")

def src_remote_deploy(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'source')
	_validate_section(config, 'deployment')
	_src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'], config['remote_user'], config['remote_host'])

def	_src_remote_rollback(dir, host, user):
	_pretty_print("[+] Starting remote rollback")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	with cd(dir):
		with settings(warn_only=True):
			if run('test -L previous').failed:
				_pretty_print('Theres nothing to rollback. Returning.', 'info')
				return
		run('mv current current.prerollback')
		run('mv previous current')
	_pretty_print("[+] Remote rollback finished")

def src_remote_rollback(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_validate_section(config, 'deployment')
	_src_remote_rollback(config['deploy_dir'], config['remote_host'], config['remote_user'])

def _deploy(config):
	_pretty_print("[+] Starting deployment.")

	try:
		if not config:
			raise NotConfiguredError

		_validate_section(config, 'source')
		_validate_section(config, 'deployment')

		_src_remote_test(config['remote_user'], config['remote_host'])
		_src_clone(config['local_dir'], config['branch'], config['git_repo'])
		_src_prepare(config['file_name'], config['local_dir'], config['branch'])
		_src_upload(config['file_name'], config['remote_user'], config['remote_host'], config['upload_dir'])
		_src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'], config['remote_user'], config['remote_host'])
		_src_remote_config(config['config_to_copy'], config['extract_dir'], config['deploy_dir'], config['remote_user'], config['remote_host'])
		_src_remote_deploy(config['extract_dir'], config['deploy_dir'], config['remote_user'], config['remote_host'])

		_pretty_print("[+] Deployment finished.")
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

def deploy(config_f = 'config.ini'):
	config = _prepare_config(config_f)

	_deploy(config)