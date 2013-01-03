#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

from __future__ import print_function

import os
import sys
import shutil
from datetime import datetime

from fabric.context_managers import cd
from fabric.state import env
from fabric.api import run, put, settings
from fabric.contrib import files

from git import Repo, InvalidGitRepositoryError
import json

from misc import *

#progress = RemoteProgress()

def _src_clone(dir='', branch = '', repo = '', date=datetime.now().strftime("%Y%m%d_%H%M%S")):
	env.host_string = 'localhost'
	pretty_print('[+] Repository clone start: %s' % dir, 'info')

	if len(dir) == 0:
		pretty_print('Directory not selected, assuming current one.', 'info')
		dir = os.getcwd()

	if os.path.isdir(dir):
		pretty_print('Directory found.', 'info')
#		shutil.move(dir, "%s-%s" %(dir, datetime.now().strftime("%Y%m%d-%H%M%S")))
	else:
		try:
			pretty_print('Directory not found, creating.', 'info')
			os.mkdir(dir)
		except:
			raise Exception('Cannot create directory %s, please create the folder manually' % dir)

	old_dir = os.getcwd()
	os.chdir(dir)

	try:
		#repo = Repo(dir)
		pretty_print('Clonning repo.', 'info')
		repo = Repo.clone_from(repo, date)
		pretty_print('Repository found. Branch: %s' % repo.active_branch, 'info')
	except InvalidGitRepositoryError: #Repo doesn't exists
		pretty_print('Repository not found. Creating new one, using %s.' % repo, 'info')
		if len(repo) == 0:
			pretty_print('Repository not selected. Returning.', 'info')
			raise InvalidGitRepositoryError
		repo = Repo.clone_from(repo, date)

	os.chdir(old_dir)
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

	pretty_print('[+] Repository clone finished', 'info')

def src_clone(config_f = 'config.ini', folder = '', date = datetime.now().strftime("%Y%m%d_%H%M%S")):
	config = prepare_config(config_f)

	config_validate_section(config, 'source')
	if len(folder):
		_src_clone(folder, config['branch'], config['git_repo'], date)
	else:
		_src_clone(config['local_dir'], config['branch'], config['git_repo'], date)

def _src_prepare(file, dir='', branch = '', date = datetime.now().strftime("%Y%m%d_%H%M%S")):
	env.host_string = 'localhost'
	pretty_print('[+] Archive prepare start. Branch: %s' % branch, 'info')

	old_dir = os.getcwd()
	os.chdir(dir)

	try:
		repo = Repo(date)
		pretty_print('Repository found.', 'info')
	except InvalidGitRepositoryError: #Repo doesn't exists
		raise Exception('Repository not found. Please provide correct one.')


	if len(branch)==0:
		pretty_print('Branch not selected. Archiving current one.', 'info')
		repo.archive(open("%s" % file,'w'))
	else:
		pretty_print('Archiving branch %s' % branch, 'info')
		repo.archive(open("%s" % file,'w'), branch)

#	except GitCommandError as ex:
#		pretty_print('Something went wrong. Message: %s' % ex.__str__())
	os.chdir(old_dir)
	pretty_print('[+] Archive prepare finished', 'info')

def src_prepare(config_f = 'config.ini', folder = '', date = ''):
	config = prepare_config(config_f)
	#1170 - change
	config_validate_section(config, 'source')

	if not len(folder):
		folder = config['local_dir']

	folder = os.path.expanduser(folder)

	if not len(date): #prepare the newest directory
		if not folder.startswith('/'):
			folder = os.path.join(os.getcwd(), folder)
		pretty_print("Folder: %s" % folder)
		all_subdirs = [os.path.join(folder, d) for d in os.listdir(folder) if os.path.isdir(os.path.join(folder,d))]
		pretty_print('Subdirs: %s' % all_subdirs)
		pretty_print("%s" % all_subdirs[0])

		date = max(all_subdirs, key=os.path.getmtime)

	pretty_print("Prepare completed, move to _src_prepare.")
	_src_prepare(config['file_name'], folder, config['branch'], date)

def _src_upload(file, user, host, dir):
	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
#	env.use_ssh_config = True
	pretty_print("[+] Starting file '%s' upload (to %s)" % (file, dir), 'info')

	pretty_print('CWD: %s' % os.getcwd())
	old_dir = os.getcwd()
	#if len(os.path.dirname(file)):
		#os.chdir(os.path.dirname(file))
	if not files.exists(dir):
		pretty_print('Target directory not found, creating.','info')
		run('mkdir -p %s' % dir)
	else:
		pretty_print('Target directory found, uploading.')

	put(file, "%s" % os.path.join(dir, os.path.basename(file)))
	pretty_print("[+] File upload finished", 'info')
	os.chdir(old_dir)

def src_upload(config_f = 'config.ini'):
	config = prepare_config(config_f)

	config_validate_section(config, 'source')
	config_validate_section(config, 'deployment')
	_src_upload(os.path.join(config['local_dir'], config['file_name']), config['remote_user'], config['remote_host'], config['upload_dir'])

def _src_clean(dir, file, to_delete):
	pretty_print('[+] Starting src_clean.', 'info')
	old_dir = os.getcwd()
	os.chdir(dir)

	if os.path.isfile(file):
		pretty_print('File %s found, deleting' % file, 'info')
		os.remove(file)

#	regexp = re.compile(r'[0-9]{8}_[0-9]{6}$')
#	f = []
#	for (dirpath, dirnames, filenames) in os.walk(dir):
#		f.extend(regexp.match(dirnames))
#		break
#	for dir in f:
	if os.path.isdir(to_delete):
		pretty_print('Directory %s found, deleting.' % to_delete)
		shutil.rmtree(to_delete)

	os.chdir(old_dir)
	pretty_print('[+] Finished src_clean.', 'info')

def _src_remote_test (user, host):
	pretty_print("[+] Starting remote test", "info")

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	run('exit 0')
	pretty_print('[+] Remote test finished', 'info')

def src_remote_test(config_f = 'config.ini'):
	config = prepare_config(config_f)

	config_validate_section(config, 'deployment')
	_src_remote_test(config['remote_user'], config['remote_host'])

def	_src_remote_extract(file, file_dir, dest_dir, user, host):
	pretty_print("[+] Starting remote extract", 'info')

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	date = datetime.now().strftime("%Y%m%d-%H%M%S")

	if not files.exists(dest_dir, verbose=True):
		pretty_print('Directory %s does not exists, creating' % dest_dir, 'info')
		run('mkdir -p %s' % dest_dir)
	else:
		pretty_print('Directory %s exists, renaming to %s-%s' % (dest_dir, dest_dir, date), 'info')
		run('mv %s %s-%s' % (dest_dir, dest_dir, date))
		run('mkdir -p %s' % dest_dir)

	#with cd(file_dir):
	pretty_print('Extracting files', 'info')
	run('tar xvf %s -C %s' % (os.path.join(file_dir, file), dest_dir))

	pretty_print("[+] Remote extract finished", 'info')

def src_remote_extract(config_f = 'config.ini', subfolder = datetime.now().strftime("%Y%m%d_%H%M%S")):
	config = prepare_config(config_f)

	config_validate_section(config, 'source')
	config_validate_section(config, 'deployment')
	#_src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'], config['remote_user'], config['remote_host'])
	_src_remote_extract(config['file_name'], config['upload_dir'], os.path.join(config['deploy_dir'], subfolder), config['remote_user'], config['remote_host'])

def _src_remote_config(json_string, src_dir, dst_dir, user, host):
	pretty_print("[+] Starting remote config copy", 'info')

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	filelist = json.loads(json_string)
	if not files.exists(dst_dir):
		pretty_print('Target directory %s does not exists. Creating.' % dst_dir, 'info')
		run('mkdir -p %s' %dst_dir)

	for object in filelist:
		if files.exists(os.path.join(src_dir, object['src']), verbose=True):
			pretty_print('Copying file %s' %object, 'info')
			run('cp -rf %s %s' % (os.path.join(src_dir, object['src']), os.path.join(dst_dir, object['dest'])))
		else:
			pretty_print('File does not exists: %s, ommiting' % os.path.join(src_dir, object['src']), 'error')

def src_remote_config(config_f = 'config.ini'):
	config = prepare_config(config_f)

	config_validate_section(config, 'source')
	config_validate_section(config, 'deployment')
	_src_remote_config(config['config_to_copy'], os.path.join(config['deploy_dir'], 'previous'), os.path.join(config['deploy_dir'], 'current'), config['remote_user'], config['remote_host'])

def	_src_remote_deploy(src_dir, dst_dir, user, host):
	pretty_print("[+] Starting remote deployment", 'info')

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	path = env.cwd

#	deploy_dir = datetime.now().strftime("%Y%m%d-%H%M%S")
#	pretty_print("current working dir: %s" % env.cwd)
#	if not files.exists(dst_dir, verbose=True):
#		run('mkdir -p %s' % dst_dir)

	#run('cp -Rfv %s %s' % (os.path.join(src_dir, "*"), dst_dir))
	with cd(dst_dir):
#		if not files.exists(deploy_dir, verbose=True):
#			run('mkdir -p %s' % deploy_dir)
#		run('cp -Rfv %s %s' % (os.path.join('..', src_dir, "*"), deploy_dir))
#		#if files.exists(os.path.join(dst_dir, 'current'), verbose=True):
		with settings(warn_only=True):
			if not run('test -L previous').failed:
				run('rm -f previous')
			pretty_print("current working dir: %s" % env.cwd)

			if not run('test -L current').failed:
				run('mv current previous')
		run('ln -s %s current' % os.path.basename(src_dir))

	pretty_print("[+] Remote deployment finished", 'info')

def src_remote_deploy(config_f = 'config.ini'):
	config = prepare_config(config_f)

	config_validate_section(config, 'source')
	config_validate_section(config, 'deployment')
	_src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'], config['remote_user'], config['remote_host'])

def	_src_remote_rollback(dir, host, user):
	pretty_print("[+] Starting remote rollback", 'info')

	env.host = host
	env.user = user
	env.host_string = "%s@%s" %(user,host)
	#	env.use_ssh_config = True

	with cd(dir):
		with settings(warn_only=True):
			if run('test -L previous').failed:
				pretty_print('Theres nothing to rollback. Returning.', 'info')
				return
		run('mv current current.prerollback')
		run('mv previous current')
	pretty_print("[+] Remote rollback finished", 'info')

def src_remote_rollback(config_f = 'config.ini'):
	config = prepare_config(config_f)

	config_validate_section(config, 'deployment')
	_src_remote_rollback(config['deploy_dir'], config['remote_host'], config['remote_user'])

def _src_pre_deploy(config):
	env.host = config['remote_host']
	env.user = config['remote_user']
	env.host_string = "%s@%s" %(env.user,env.host)

	pretty_print("[+] Starting remote pre-deploy command", 'info')

	if not len(config['pre_deploy']):
		raise Exception('Pre_deploy command not provided')

	_src_remote_test(env.user, env.host)
	run(config['pre_deploy'])

	pretty_print("[+] Remote pre-deploy command finished", 'info')

def src_pre_deploy(config_f='config.ini'):
	config = prepare_config(config_f)
	config_validate_section(config, 'deployment')
	_src_pre_deploy(config)

def _src_post_deploy(config):
	env.host = config['remote_host']
	env.user = config['remote_user']
	env.host_string = "%s@%s" %(env.user,env.host)

	pretty_print("[+] Starting remote post-deploy command", 'info')

	if not len(config['post_deploy']):
		raise Exception('Post_deploy command not provided')

	_src_remote_test(env.user, env.host)
	run(config['post_deploy'])

	pretty_print("[+] Remote post-deploy command finished", 'info')

def src_post_deploy(config_f='config.ini'):
	config = prepare_config(config_f)
	config_validate_section(config, 'deployment')
	_src_post_deploy(config)

def _deploy(config):
	pretty_print("[+] Starting deployment.", 'info')

	try:
		if not config:
			raise NotConfiguredError('Deploy - config not provided')

		date = datetime.now().strftime("%Y%m%d_%H%M%S")

		config_validate_section(config, 'source')
		config_validate_section(config, 'deployment')

		_src_remote_test(config['remote_user'], config['remote_host'])
		_src_pre_deploy(config)
		_src_clone(config['local_dir'], config['branch'], config['git_repo'], date)
		_src_prepare(config['file_name'], config['local_dir'], config['branch'], date)
		_src_upload(os.path.join(config['local_dir'], config['file_name']), config['remote_user'], config['remote_host'], config['upload_dir'])
		_src_remote_extract(config['file_name'], config['upload_dir'], os.path.join(config['deploy_dir'], date), config['remote_user'], config['remote_host'])
		_src_remote_deploy(os.path.join(config['deploy_dir'], date), config['deploy_dir'], config['remote_user'], config['remote_host'])
		_src_remote_config(config['config_to_copy'], os.path.join(config['deploy_dir'], 'previous'), os.path.join(config['deploy_dir'], date), config['remote_user'], config['remote_host'])
		_src_post_deploy(config)

		pretty_print('Cleaning flag: %s' % config['upload_clean'].lower())
		if config['upload_clean'].lower() == 'true' or config['upload_clean'] == '1':
			_src_clean(config['local_dir'], config['file_name'], date)
		else:
			pretty_print('Cleaning not selected, omitting.', 'info')
		pretty_print("[+] Deployment finished.", 'info')
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue), 'error')

def deploy(config_f = 'config.ini'):
	config = prepare_config(config_f)

	_deploy(config)
