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

from misc import *

def validate_config(config, section):
	pretty_print("Validating %s config section" % section, 'debug')

	if section == 'source' :
		if not 'source' in config:
			raise NotConfiguredError("Source section does not exists")

		if not 'git' in config['source']:
			raise NotConfiguredError("Section \"git\" does not exists")

		if not 'dirs' in config['source']['git']:
			pretty_print("No dirs selected, archiving whole repo", "info")
			config['source']['git']['dirs'] = []

		if not 'repo' in config['source']['git'] or not len(config['source']['git']['repo']):
			raise NotConfiguredError("Repository not set")

		if not 'branch' in config['source']['git'] or not len(config['source']['git']['branch']):
			pretty_print("Repository branch not set. Clone from \"master\"", 'info')
			config['source']['git']['branch'] = 'master'

		if not 'local' in config['source']['git']:
			pretty_print("git local repo not set. Using current date as repo", 'info')
			config['source']['git']['local'] = ""

		if not 'local' in config['source'] or not len(config['source']['local']):
			pretty_print("Local directory not set. Use current working directory", 'info')
			config['source']['local'] = os.getcwd()
		config['source']['local'] = os.path.expanduser(config['source']['local'])

		if not 'file' in config['source'] or not len(config['source']['file']):
			pretty_print("Archive file not set, using src.tar", 'info')
			config['source']['file'] = 'src.tar'

		config['source']['file'] = os.path.expanduser(config['source']['file'])

	elif section == 'remote' :
		if not 'remote' in config:
			raise NotConfiguredError("Remote section does not exists")

		if not 'host' in config['remote'] or not len(config['remote']['host']):
			raise NotConfiguredError("Host not set.")

		if not 'user' in config['remote'] or not len(config['remote']['user']):
			raise NotConfiguredError("User not set.")

		if not 'port' in config['remote'] :
			pretty_print("Port not set. Using 22", 'info')
			config['remote']['port'] = 22
			env.port = config['remote']['port']

		if not 'dir' in config['remote'] :
			pretty_print("Dir not set.", 'info')
			config['remote']['dir'] = ""

		if not 'clean' in config['remote'] :
			pretty_print("Clean not set. No clean by default", 'info')
			config['remote']['clean'] = False

	elif section == 'config':
		if not 'config' in config:
			raise NotConfiguredError('No section "config" in config.')

		if not 'dir' in config['deploy'] or not len(config['deploy']['dir']):
			raise NotConfiguredError('No directory selected in deploy section.')

		if not 'pre' in config['deploy']:
			pretty_print("No pre-deploy commmands", "info")
			config['deploy']['pre'] = []

		if not type(config['deploy']['pre']) == type(list()):
			raise Exception("Wrong format of 'pre' section - should be list")

		if not 'post' in config['deploy']:
			pretty_print("No post-deploy commmands", "info")
			config['deploy']['post'] = []

		if not type(config['deploy']['post']) == type(list()):
			raise Exception("Wrong format of 'post' section - should be list")

	elif section == 'deploy':
		if not 'deploy' in config:
			raise NotConfiguredError('No section "deploy" in config.')

	pretty_print('Config is valid!', 'debug')

	return config

def _src_clone(directory='', branch = '', repo = '', date=datetime.now().strftime("%Y%m%d_%H%M%S")):
	env.host_string = 'localhost'
	pretty_print('[+] Repository clone start: %s' % directory, 'info')

	if len(directory) == 0:
		pretty_print('Directory not selected, assuming current one.', 'info')
		directory = os.getcwd()

	if os.path.isdir(directory):
		pretty_print('Directory found.', 'info')
	else:
		try:
			pretty_print('Directory not found, creating.', 'info')
			os.mkdir(directory)
		except:
			raise Exception('Cannot create directory %s, please create the folder manually' % directory)

	old_dir = os.getcwd()
	os.chdir(directory)

	try:
		if not os.path.isdir("%s/.git" % date): #repo = Repo(dir)
			raise InvalidGitRepositoryError()

		repo = Repo(date)

		pretty_print('Repository found. Branch: %s' % repo.active_branch, 'info')

	except InvalidGitRepositoryError: #Repo doesn't exists
		pretty_print('Repository not found. Creating new one, using %s.' % repo, 'info')
		if len(repo) == 0:
			pretty_print('Repository not selected. Returning.', 'info')
			raise InvalidGitRepositoryError
		repo = Repo.clone_from(repo, date)

	if not len(branch):
		branch = repo.active_branch

	if repo.active_branch is not branch:
		pretty_print('Changing branch', 'info')
		repo.git.checkout('master')

	pretty_print('Pulling changes', 'info')
	repo.git.pull('origin', branch)

	os.chdir(old_dir)
	#repo.create_remote('origin', config.GIT_REPO)

	pretty_print('[+] Repository clone finished', 'info')

def src_clone(config_f = 'config.json', folder = '', date = datetime.now().strftime("%Y%m%d_%H%M%S")):
	config = prepare_config(config_f)
	config = validate_config(config, 'source')

	if len(config['source']['git']['local']):
		repo = config['source']['git']['local']
		pretty_print("using config['source']['git']['local']")
	else:
		repo = date
		pretty_print("using date")

	if len(folder):
		_src_clone(folder, config['source']['git']['branch'], config['source']['git']['repo'], repo)
	else:
		_src_clone(config['source']['local'], config['source']['git']['branch'], config['source']['git']['repo'], repo)

def _src_prepare(file, directory='', branch = '', date = datetime.now().strftime("%Y%m%d_%H%M%S"), dirs=[]):
	env.host_string = 'localhost'
	pretty_print('[+] Archive prepare start. Branch: %s' % branch, 'info')

	old_dir = os.getcwd()
	os.chdir(directory)

	try:
		repo = Repo(date)
		pretty_print('Repository found.', 'info')
	except InvalidGitRepositoryError: #Repo doesn't exists
		raise Exception('Repository not found. Please provide correct one.')

	pretty_print('Archiving current branch.', 'info')

	compression = file.split('.')
	pretty_print("cwd: %s" % os.getcwd())

	if (compression[-1] == "gz" and compression[-2] == "tar") or compression[-1] == "tgz":
		repo.git.archive('--o', os.path.join(os.getcwd(),file), '--format',"tar.gz", 'HEAD', '' if not len(dirs) else ''.join(dirs))
	elif compression[-1] == "tar":
		repo.git.archive('--o', os.path.join(os.getcwd(),file), '--format',"tar", 'HEAD', '' if not len(dirs) else ''.join(dirs))
	else:
		raise Exception("Unknown file format. Supported: tar, tar.gz, tgz")

	os.chdir(old_dir)
	pretty_print('[+] Archive prepare finished', 'info')

def src_prepare(config_f = 'config.json', folder = '', date = ''):
	config = prepare_config(config_f)
	config = validate_config(config, 'source')

	if not len(folder):
		folder = config['source']['local']

	folder = os.path.expanduser(folder)

	if not len(date): #prepare the newest directory
		pretty_print("Subfolder not provided, assuming newest.", 'info')
		if not folder.startswith('/'):
			folder = os.path.join(os.getcwd(), folder)
		pretty_print("Folder: %s" % folder)
		all_subdirs = [os.path.join(folder, d) for d in os.listdir(folder) if os.path.isdir(os.path.join(folder,d))]
		pretty_print('Subdirs: %s' % all_subdirs)
		pretty_print("%s" % all_subdirs[0])

		date = max(all_subdirs, key=os.path.getmtime)

	pretty_print("Prepare completed, move to _src_prepare.")
	_src_prepare(config['source']['file'], folder, config['source']['git']['branch'], date, config['source']['git']['dirs'])

def _src_upload(to_upload, user, host, directory):
	env.host = host
	env.user = user
	env.host_string = "%s@%s:%s" %(env.user,env.host, env.port)

	pretty_print("[+] Starting file '%s' upload (to %s)" % (to_upload, directory), 'info')

	pretty_print('CWD: %s' % os.getcwd())
	old_dir = os.getcwd()

	if not files.exists(directory):
		pretty_print('Target directory not found, creating.','info')
		run('mkdir -p %s' % directory)
	else:
		pretty_print('Target directory found, uploading.')

	put(to_upload, "%s" % os.path.join(directory, os.path.basename(to_upload)))
	pretty_print("[+] File upload finished", 'info')
	os.chdir(old_dir)

def src_upload(config_f = 'config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, 'source')
	config = validate_config(config, 'remote')

	_src_upload(os.path.join(config['source']['local'], config['source']['file']), config['remote']['user'], config['remote']['host'], config['remote']['dir'])

def _src_clean(directory, file, to_delete):
	pretty_print('[+] Starting src_clean.', 'info')
	old_dir = os.getcwd()
	os.chdir(directory)

	if os.path.isfile(file):
		pretty_print('File %s found, deleting' % file, 'info')
		os.remove(file)

	if os.path.isdir(to_delete):
		pretty_print('Directory %s found, deleting.' % to_delete, 'info')
		shutil.rmtree(to_delete)

	os.chdir(old_dir)
	pretty_print('[+] Finished src_clean.', 'info')

def _src_remote_test (user, host):
	pretty_print("[+] Starting remote test", "info")

	env.host = host
	env.user = user
	env.host_string = "%s@%s:%s" %(env.user,env.host, env.port)
	#	env.use_ssh_config = True

	run('exit 0')
	pretty_print('[+] Remote test finished', 'info')

def src_remote_test(config_f = 'config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, 'remote')

	_src_remote_test(config['remote']['user'], config['remote']['host'])

def	_src_remote_extract(file, file_dir, dest_dir, user, host):
	pretty_print("[+] Starting remote extract", 'info')
	pretty_print("Extracting to directory %s" % dest_dir)
	env.host = host
	env.user = user
	env.host_string = "%s@%s:%s" %(env.user,env.host, env.port)
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

	compression = file.split('.')
	if (compression[-1] == "gz" and compression[-2] == "tar") or compression[-1] == "tgz":
		run('tar xvfz %s -C %s' % (os.path.join(file_dir, file), dest_dir))
	# elif compression[-1] == "bz2" and compression[-2] == "tar":
	# 	run('tar xvfj %s -C %s' % (os.path.join(file_dir, file), dest_dir))
	elif compression[-1] == "tar":
		run('tar xvf %s -C %s' % (os.path.join(file_dir, file), dest_dir))
	else:
		pretty_print("Unknown file format. Supported: tar, tar.gz, tgz", "error")


	pretty_print("[+] Remote extract finished", 'info')

def src_remote_extract(config_f = 'config.json', subfolder = datetime.now().strftime("%Y%m%d_%H%M%S")):
	config = prepare_config(config_f)
	config = validate_config(config, 'source')
	config = validate_config(config, 'remote')

	#_src_remote_extract(config['file_name'], config['upload_dir'], config['extract_dir'], config['remote_user'], config['remote_host'])
	#_src_remote_extract(config['source']['file'], config['upload_dir'], os.path.join(config['deploy_dir'], subfolder), config['remote_user'], config['remote_host'])
	_src_remote_extract(config['source']['file'], config['remote']['dir'], os.path.join(config['deploy']['dir'], subfolder), config['remote']['user'], config['remote']['host'])

def _src_remote_config(to_copy, user, host):
	pretty_print("[+] Starting remote config copy", 'info')

	env.host = host
	env.user = user
	env.host_string = "%s@%s:%s" %(env.user,env.host, env.port)
	#	env.use_ssh_config = True

	for key, value in to_copy.iteritems():
		(head,tail) = os.path.split(value['dst'])
		if not files.exists(head):
			pretty_print('Target directory %s does not exists. Creating.' % head, 'info')
			run('mkdir -p %s' % head)

		if files.exists(value['src'], verbose=True):
			pretty_print('Copying %s' % key, 'info')
			run('cp -rf %s %s' % (value['src'], value['dst']))
		else:
			pretty_print('File does not exists: %s, ommiting' % value['src'], 'error')

def src_remote_config(config_f = 'config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, 'config')
	config = validate_config(config, 'remote')

	_src_remote_config(config['config'], config['remote']['user'], config['remote']['host'])

def	_src_remote_deploy(src_dir, dst_dir, user, host):
	pretty_print("[+] Starting remote deployment", 'info')

	env.host = host
	env.user = user
	env.host_string = "%s@%s:%s" %(env.user,env.host, env.port)

	path = env.cwd

	with cd(dst_dir):
		with settings(warn_only=True):
			if not run('test -L previous').failed:
				run('rm -f previous')
			pretty_print("current working dir: %s" % env.cwd)

			if not run('test -L current').failed:
				run('mv current previous')
		run('ln -s %s current' % os.path.basename(src_dir))

	pretty_print("[+] Remote deployment finished", 'info')

def src_remote_deploy(config_f = 'config.json', directory = ''):
	config = prepare_config(config_f)
	config = validate_config(config, 'remote')
	config = validate_config(config, 'deploy')

	if not len(directory):
		raise Exception("Source directory not provided.")

	_src_remote_deploy(directory, config['deploy']['dir'], config['remote']['user'], config['remote']['host'])

def	_src_remote_rollback(dir, host, user):
	pretty_print("[+] Starting remote rollback", 'info')

	env.host = host
	env.user = user
	env.host_string = "%s@%s:%s" %(env.user,env.host, env.port)
	#	env.use_ssh_config = True

	with cd(dir):
		with settings(warn_only=True):
			if run('test -L previous').failed:
				pretty_print('Theres nothing to rollback. Returning.', 'info')
				return
		run('mv current current.prerollback')
		run('mv previous current')
	pretty_print("[+] Remote rollback finished", 'info')

def src_remote_rollback(config_f = 'config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, 'remote')
	config = validate_config(config, 'deploy')

	_src_remote_rollback(config['deploy']['dir'], config['remote']['host'], config['remote']['user'])

def _src_pre_deploy(command_list, user, host):
	env.host = host
	env.user = user
	env.host_string = "%s@%s:%s" %(env.user,env.host, env.port)

	pretty_print("[+] Starting remote pre-deploy commands", 'info')

	if not len(command_list):
		pretty_print('Pre_deploy commands not provided', 'info')
		return

	_src_remote_test(env.user, env.host)
	for i in command_list:
		run(i)

	pretty_print("[+] Remote pre-deploy command finished", 'info')

def src_pre_deploy(config_f='config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, 'remote')
	config = validate_config(config, 'deploy')

	_src_pre_deploy(config['deploy']['pre'], config['remote']['user'], config['remote']['host'])

def _src_post_deploy(command_list, user, host):
	env.host = host
	env.user = user
	env.host_string = "%s@%s:%s" %(env.user,env.host, env.port)

	pretty_print("[+] Starting remote post-deploy commands", 'info')

	if not len(command_list):
		pretty_print('Post_deploy commands not provided', 'info')
		return

	_src_remote_test(env.user, env.host)
	for i in command_list:
		run(i)

	pretty_print("[+] Remote post-deploy command finished", 'info')

def src_post_deploy(config_f='config.json'):
	config = prepare_config(config_f)
	config = validate_config(config, 'remote')
	config = validate_config(config, 'deploy')

	_src_post_deploy(config['deploy']['post'], config['remote']['user'], config['remote']['host'])


def _deploy(config, subdir = ''):
	pretty_print("[+] Starting deployment.", 'info')

	try:
		if not config:
			raise NotConfiguredError('Deploy - config not provided')

		date = datetime.now().strftime("%Y%m%d_%H%M%S")

		if len(subdir):
			repo = subdir
			pretty_print('using provided subdir')
		else:
			if len(config['source']['git']['local']):
				repo = config['source']['git']['local']
				pretty_print("using config['source']['git']['local']")
			else:
				repo = date
				pretty_print("using date")

		_src_remote_test(config['remote']['user'], config['remote']['host'])
		_src_pre_deploy(config['deploy']['pre'], config['remote']['user'], config['remote']['host'])
		_src_clone(config['source']['local'], config['source']['git']['branch'], config['source']['git']['repo'], repo)
		_src_prepare(config['source']['file'], config['source']['local'], config['source']['git']['branch'], repo, config['source']['git']['dirs'])
		_src_upload(os.path.join(config['source']['local'], config['source']['file']), config['remote']['user'], config['remote']['host'], config['remote']['dir'])
		_src_remote_extract(config['source']['file'], config['remote']['dir'], os.path.join(config['deploy']['dir'], date), config['remote']['user'], config['remote']['host'])
		_src_remote_deploy(os.path.join(config['deploy']['dir'], date), config['deploy']['dir'], config['remote']['user'], config['remote']['host'])
		_src_remote_config(config['config'], config['remote']['user'], config['remote']['host'])
		_src_post_deploy(config['deploy']['post'], config['remote']['user'], config['remote']['host'])

		pretty_print('Cleaning flag: %s' % config['remote']['clean'])
		if config['remote']['clean']:
			_src_clean(config['source']['local'], config['source']['file'], date)
		else:
			pretty_print('Cleaning not selected, omitting.', 'info')
		pretty_print("[+] Deployment finished.", 'info')
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue), 'error')

def deploy(config_f = 'config.json', subfolder = ''):
	config = prepare_config(config_f)
	config = validate_config(config, 'remote')
	config = validate_config(config, 'deploy')
	config = validate_config(config, 'config')
	config = validate_config(config, 'source')

	pretty_print("Deploy subfolder: %s" % subfolder)

	_deploy(config, subfolder)
