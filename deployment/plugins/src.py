#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

from __future__ import print_function

import shutil
from datetime import datetime

from fabric.context_managers import cd
from fabric.api import put, settings
from fabric.contrib import files

from git import Repo, InvalidGitRepositoryError

from deployment.libs.gitarchive import GitArchiver
from deployment.common import *
from deployment.plugin import Plugin


class SrcClone(Plugin):
    command = 'src_clone'
    config = None
    description = 'Arguments: <folder> <subfolder> - clone repo to subfolder in local folder'

    def validate_config(self):
        if not 'source' in config:
            raise NotConfiguredError("Source section does not exists")

        if not 'git' in config['source']:
            raise NotConfiguredError("Section \"git\" does not exists")

        if not 'repo' in config['source']['git'] or not len(config['source']['git']['repo']):
            pretty_print("Repository not set. Assuming current dir has a git repo", 'info')
            try:
                g = Repo(os.getcwd())
                config['source']['git']['repo'] = g.remotes.origin.url
            except InvalidGitRepositoryError:
                raise NotConfiguredError("No repo provided, and not in tracked directory")

        if not 'branch' in config['source']['git'] or not len(config['source']['git']['branch']):
            pretty_print("Repository branch not set. Clone from \"master\"", 'info')
            config['source']['git']['branch'] = 'master'

        if not 'local' in config['source']['git']:
            pretty_print("git local repo not set. Using current folder as repo", 'info')
            config['source']['git']['local'] = os.getcwd()

        config['source']['git']['local'] = os.path.expanduser(config['source']['git']['local'])

        if not 'local' in config['source'] or not len(config['source']['local']):
            pretty_print("Local directory not set. Use current working directory", 'info')
            config['source']['local'] = os.getcwd()
        config['source']['local'] = os.path.expanduser(config['source']['local'])

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            local_directory = args[0]
        except IndexError:
            local_directory = config['source']['local']

        try:
            repo_directory = args[1]
        except IndexError:
            repo_directory = config['source']['git']['local']

        branch = config['source']['git']['branch']
        repo = config['source']['git']['repo']

        env.host_string = 'localhost'
        pretty_print('[+] Repository clone start: %s' % local_directory, 'info')

        # if not len(directory):
        #     pretty_print('Directory not selected, assuming current one.', 'info')
        #     directory = os.getcwd()

        # if os.path.isdir(directory):
        #     pretty_print('Directory found.', 'info')
        # else:
            # try:
            #     pretty_print('Directory not found, creating.', 'info')
            #     os.mkdir(directory)
            # except:
            #     raise Exception('Cannot create directory %s, please create the folder manually' % directory)

        old_dir = os.getcwd()
        os.chdir(local_directory)

        try:
            if not os.path.isdir("%s/.git" % repo_directory):  # repo = Repo(dir)
                if os.path.isdir(repo_directory):
                    raise IOError('Directory already exists and is not repository. Clone will fail. Please check your '
                                  'configuration')
                raise InvalidGitRepositoryError()

            repo = Repo(repo_directory)

            pretty_print('Repository found. Branch: %s' % repo.active_branch, 'info')

        except InvalidGitRepositoryError:  # Repo doesn't exists
            pretty_print('Repository not found. Creating new one, using %s.' % repo, 'info')
            if len(repo) == 0:
                pretty_print('Repository not selected. Returning.', 'info')
                raise InvalidGitRepositoryError
            repo = Repo.clone_from(repo, repo_directory)

        if not len(branch):
            branch = repo.active_branch

        if repo.active_branch is not branch:
            pretty_print('Changing branch', 'info')
            repo.git.checkout('master')

        pretty_print('Pulling changes', 'info')
        repo.git.pull('origin', branch)

        pretty_print('Fetching submodules', 'info')
        repo.git.submodule("init")
        repo.submodule_update(init=True)

        os.chdir(old_dir)
        #repo.create_remote('origin', config.GIT_REPO)

        pretty_print('[+] Repository clone finished', 'info')


class SrcPrepare(Plugin):
    command = 'src_prepare'
    config = None
    description = 'Arguments: <folder> <subfolder> - archive repo from subfolder in local folder to file'

    def validate_config(self):
        if not 'source' in config:
            raise NotConfiguredError("Source section does not exists")

        if not 'git' in config['source']:
            raise NotConfiguredError("Section \"git\" does not exists")

        if not 'dirs' in config['source']['git']:
            pretty_print("No dirs selected, archiving whole repo", "info")
            config['source']['git']['dirs'] = []

        if not 'branch' in config['source']['git'] or not len(config['source']['git']['branch']):
            pretty_print("Repository branch not set. Clone from \"master\"", 'info')
            config['source']['git']['branch'] = 'master'

        if not 'file' in config['source'] or not len(config['source']['file']):
            pretty_print("Archive file not set, using src.tar.gz", 'info')
            config['source']['file'] = 'src.tar.gz'

        config['source']['file'] = os.path.expanduser(config['source']['file'])

    def run(self, *args, **kwargs):
        self.validate_config()

        archive_file = config['source']['file']
        branch = config['source']['git']['branch']
        dirs = config['source']['git']['dirs']

        try:
            local_directory = os.path.expanduser(args[0])
        except IndexError:
            local_directory = config['source']['local']

        try:
            repo_directory = os.path.expanduser(args[1])
        except IndexError:
            repo_directory = config['source']['git']['local']

        env.host_string = 'localhost'
        pretty_print('[+] Archive prepare start. Branch: %s' % branch, 'info')

        old_dir = os.getcwd()
        os.chdir(local_directory)

        try:
            repo = Repo(repo_directory)
            pretty_print('Repository found.', 'info')
        except InvalidGitRepositoryError:  # Repo doesn't exists
            raise NotConfiguredError('Repository not found. Please provide correct one.')

        pretty_print('Archiving current branch.', 'info')

        # compression = file.split('.')
        pretty_print("cwd: %s" % os.getcwd())

        archiver = GitArchiver(main_repo_abspath=os.path.join(os.getcwd(), repo_directory), include_dirs=dirs)
        archiver.create(os.path.join(os.getcwd(), archive_file))

        # if (compression[-1] == "gz" and compression[-2] == "tar") or compression[-1] == "tgz":
        #     repo.git.archive-all('--o', os.path.join(os.getcwd(), file), '--format', "tar.gz", 'HEAD',
        #                          '' if not len(dirs) else dirs)
        # elif compression[-1] == "tar":
        #     repo.git.archive-all('--o', os.path.join(os.getcwd(), file), '--format', "tar", 'HEAD',
        #                          '' if not len(dirs) else dirs)
        # else:
        #     raise Exception("Unknown file format. Supported: tar, tar.gz, tgz")

        os.chdir(old_dir)
        pretty_print('[+] Archive prepare finished', 'info')


class SrcUpload(Plugin):
    command = 'src_upload'
    config = None
    description = 'Arguments: none - upload packed file from local folder to remote host'

    def validate_config(self):
        if not 'local' in config['source'] or not len(config['source']['local']):
            pretty_print("Local directory not set. Use current working directory", 'info')
            config['source']['local'] = os.getcwd()
        config['source']['local'] = os.path.expanduser(config['source']['local'])

        if not 'file' in config['source'] or not len(config['source']['file']):
            pretty_print("Archive file not set, using src.tar.gz", 'info')
            config['source']['file'] = 'src.tar.gz'

        config['source']['file'] = os.path.expanduser(config['source']['file'])

        if not 'remote' in config:
            raise NotConfiguredError("Remote section does not exists")

        if not 'host' in config['remote'] or not len(config['remote']['host']):
            raise NotConfiguredError("Host not set.")

        if not 'user' in config['remote'] or not len(config['remote']['user']):
            raise NotConfiguredError("User not set.")

        if not 'port' in config['remote']:
            pretty_print("Port not set. Using 22", 'info')
            config['remote']['port'] = 22
        env.port = config['remote']['port']

        if not 'dir' in config['remote']:
            pretty_print("Dir not set. Using /tmp/ as default", 'info')
            config['remote']['dir'] = "/tmp/"

    def run(self, *args, **kwargs):
        self.validate_config()

        to_upload = os.path.join(config['source']['local'], config['source']['file'])
        user = config['remote']['user']
        host = config['remote']['host']
        remote_directory = config['remote']['dir']

        env.host = host
        env.user = user
        env.port = config['remote']['port']
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        pretty_print("[+] Starting file '%s' upload (to %s)" % (to_upload, remote_directory), 'info')

        pretty_print('CWD: %s' % os.getcwd())
        old_dir = os.getcwd()

        if not files.exists(remote_directory):
            pretty_print('Target directory not found, creating.', 'info')
            run('mkdir -p %s' % remote_directory)
        else:
            pretty_print('Target directory found, uploading.')

        put(to_upload, "%s" % os.path.join(remote_directory, os.path.basename(to_upload)))
        pretty_print("[+] File upload finished", 'info')
        os.chdir(old_dir)


class SrcClean(Plugin):
    command = 'src_clean'
    config = None
    description = 'Arguments: <to_delete> - delete file/folder provided as argument'

    def validate_config(self):
        if not 'local' in config['source'] or not len(config['source']['local']):
            pretty_print("Local directory not set. Use current working directory", 'info')
            config['source']['local'] = os.getcwd()
        config['source']['local'] = os.path.expanduser(config['source']['local'])

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            to_delete = args[0]
        except IndexError:
            raise NotConfiguredError("src_clean need arg 'to_delete' ")
        local_directory = config['source']['local']

        pretty_print('[+] Starting src_clean.', 'info')

        old_dir = os.getcwd()
        os.chdir(local_directory)

        if os.path.isfile(to_delete):
            pretty_print('File %s found, deleting' % to_delete, 'info')
            os.remove(to_delete)

        if os.path.isdir(to_delete):
            pretty_print('Directory %s found, deleting.' % to_delete, 'info')
            shutil.rmtree(to_delete)

        os.chdir(old_dir)
        pretty_print('[+] Finished src_clean.', 'info')


class SrcRemoteCheck(Plugin):
    command = 'src_remote_test'
    config = None
    description = 'Arguments: <user> <host> - test remote host'

    def validate_config(self):
        if not 'remote' in config:
            raise NotConfiguredError("Remote section does not exists")

        if not 'host' in config['remote'] or not len(config['remote']['host']):
            raise NotConfiguredError("Host not set.")

        if not 'user' in config['remote'] or not len(config['remote']['user']):
            raise NotConfiguredError("User not set.")

        if not 'port' in config['remote']:
            pretty_print("Port not set. Using 22", 'info')
            config['remote']['port'] = 22
        env.port = config['remote']['port']

    def run(self, *args, **kwargs):
        try:
            user = args[0]
        except IndexError:
            user = config['remote']['user']

        try:
            host = args[1]
        except IndexError:
            host = config['remote']['host']

        pretty_print("[+] Starting remote test", "info")

        env.host = host
        env.user = user
        env.port = config['remote']['port']
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)
        #	env.use_ssh_config = True

        run('exit 0')
        pretty_print('[+] Remote test finished', 'info')


class SrcRemoteExtract(Plugin):
    command = 'src_remote_extract'
    config = None
    description = 'Arguments: <subfolder> - extract uploaded file to selected subfolder of deploy_dir, ' \
                  'default current date'

    def validate_config(self):
        if not 'file' in config['source'] or not len(config['source']['file']):
            pretty_print("Archive file not set, using src.tar", 'info')
            config['source']['file'] = 'deployment.tar.gz'

        config['source']['file'] = os.path.expanduser(config['source']['file'])

        if not 'remote' in config:
            raise NotConfiguredError("Remote section does not exists")

        if not 'host' in config['remote'] or not len(config['remote']['host']):
            raise NotConfiguredError("Host not set.")

        if not 'user' in config['remote'] or not len(config['remote']['user']):
            raise NotConfiguredError("User not set.")

        if not 'port' in config['remote']:
            pretty_print("Port not set. Using 22", 'info')
            config['remote']['port'] = 22
        env.port = config['remote']['port']

        if not 'deploy' in config:
            raise NotConfiguredError('No section "deploy" in config.')
        if not 'dir' in config['deploy'] or not len(config['deploy']['dir']):
            config['deploy']['dir'] = 'app'

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            subfolder = args[0]
        except IndexError:
            subfolder = datetime.now().strftime("%Y%m%d_%H%M%S")

        user = config['remote']['user']
        host = config['remote']['host']
        port = config['remote']['port']
        uploaded_file = config['source']['file']
        file_dir = config['remote']['dir']  # where file is uploaded
        dest_dir = os.path.join(config['deploy']['dir'], subfolder)  # where should be unpacked

        pretty_print("[+] Starting remote extract", 'info')
        pretty_print("Extracting to directory %s" % dest_dir)
        env.host = host
        env.user = user
        env.port = port

        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)
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

        compression = uploaded_file.split('.')
        if (compression[-1] == "gz" and compression[-2] == "tar") or compression[-1] == "tgz":
            run('tar xvfz %s -C %s' % (os.path.join(file_dir, uploaded_file), dest_dir))
        # elif compression[-1] == "bz2" and compression[-2] == "tar":
        # 	run('tar xvfj %s -C %s' % (os.path.join(file_dir, file), dest_dir))
        elif compression[-1] == "tar":
            run('tar xvf %s -C %s' % (os.path.join(file_dir, uploaded_file), dest_dir))
        else:
            raise Exception("Unknown file format. Supported: tar, tar.gz, tgz")


class SrcRemoteConfig(Plugin):
    command = 'src_remote_config'
    config = None
    description = 'Arguments: None - copy config from previous to current'

    def validate_config(self):
        if not 'remote' in config:
            raise NotConfiguredError("Remote section does not exists")

        if not 'host' in config['remote'] or not len(config['remote']['host']):
            raise NotConfiguredError("Host not set.")

        if not 'user' in config['remote'] or not len(config['remote']['user']):
            raise NotConfiguredError("User not set.")

        if not 'port' in config['remote']:
            pretty_print("Port not set. Using 22", 'info')
            config['remote']['port'] = 22
        env.port = config['remote']['port']

        if not 'config' in config:
            raise NotConfiguredError('No section "config" in config.')

    def run(self, *args, **kwargs):
        self.validate_config()

        user = config['remote']['user']
        host = config['remote']['host']
        port = config['remote']['port']
        base_dir = config['deploy']['dir']
        to_copy = config['config']

        pretty_print("[+] Starting remote config copy", 'info')

        env.host = host
        env.user = user
        env.port = port
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)
        #	env.use_ssh_config = True
        if isinstance(to_copy, dict):
            for key, value in to_copy.iteritems():
                (head, tail) = os.path.split(value['dst'])
                if not files.exists(head):
                    pretty_print('Target directory %s does not exists. Creating.' % head, 'info')
                    run('mkdir -p %s' % head)

                if files.exists(value['src'], verbose=True):
                    pretty_print('Copying %s' % key, 'info')
                    run('cp -rf %s %s' % (value['src'], value['dst']))
                else:
                    pretty_print('File does not exists: %s, ommiting' % value['src'], 'error')
        elif isinstance(to_copy, list):
            base_from = os.path.join(base_dir, 'previous')
            base_to = os.path.join(base_dir, 'current')

            for item in to_copy:
                (path, filename) = os.path.split(item)
                from_file = os.path.join(base_from, item)
                to_file = os.path.join(base_to, item)
                to_dir = os.path.join(base_to, path)

                if not files.exists(to_dir):
                    pretty_print('Target directory %s does not exists. Creating.' % path, 'info')
                    run('mkdir -p %s' % to_dir)

                if files.exists(from_file, verbose=True):
                    pretty_print('Copying %s' % filename, 'info')
                    run('cp -rf %s %s' % (from_file, to_file))
                else:
                    pretty_print('File does not exists: %s, ommiting' % filename, 'error')

        else:
            raise NotConfiguredError("Wrong 'config' section format")


class SrcRemoteDeploy(Plugin):
    command = 'src_remote_deploy'
    config = None
    description = 'Arguments: <subfolder> - deploys new version'

    def validate_config(self):
        if not 'remote' in config:
            raise NotConfiguredError("Remote section does not exists")

        if not 'host' in config['remote'] or not len(config['remote']['host']):
            raise NotConfiguredError("Host not set.")

        if not 'user' in config['remote'] or not len(config['remote']['user']):
            raise NotConfiguredError("User not set.")

        if not 'port' in config['remote']:
            pretty_print("Port not set. Using 22", 'info')
            config['remote']['port'] = 22
        env.port = config['remote']['port']

        if not 'deploy' in config:
            raise NotConfiguredError('No section "deploy" in config.')

        if not 'dir' in config['deploy'] or not len(config['deploy']['dir']):
            config['deploy']['dir'] = 'app'

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            src_dir = args[0]
        except IndexError:
            raise NotConfiguredError('You need to provide folder which will be deployed')

        user = config['remote']['user']
        host = config['remote']['host']
        port = config['remote']['port']
        dst_dir = config['deploy']['dir']

        pretty_print("[+] Starting remote deployment", 'info')

        env.host = host
        env.user = user
        env.port = port
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        with cd(dst_dir):
            with settings(warn_only=True):
                if not run('test -L previous').failed:
                    run('rm -f previous')
                pretty_print("current working dir: %s" % env.cwd)

                if not run('test -L current').failed:
                    run('mv current previous')
            run('ln -s %s current' % os.path.basename(src_dir))

        pretty_print("[+] Remote deployment finished", 'info')


class SrcRemoteRollback(Plugin):
    command = 'src_remote_rollback'
    config = None
    description = 'Arguments: None - backs to previous version'

    def validate_config(self):
        if not 'remote' in config:
            raise NotConfiguredError("Remote section does not exists")

        if not 'host' in config['remote'] or not len(config['remote']['host']):
            raise NotConfiguredError("Host not set.")

        if not 'user' in config['remote'] or not len(config['remote']['user']):
            raise NotConfiguredError("User not set.")

        if not 'port' in config['remote']:
            pretty_print("Port not set. Using 22", 'info')
            config['remote']['port'] = 22
        env.port = config['remote']['port']

        if not 'deploy' in config:
            raise NotConfiguredError('No section "deploy" in config.')

        if not 'dir' in config['deploy'] or not len(config['deploy']['dir']):
            config['deploy']['dir'] = 'app'

    def run(self, *args, **kwargs):
        self.validate_config()

        user = config['remote']['user']
        host = config['remote']['host']
        port = config['remote']['port']
        remote_dir = config['deploy']['dir']

        pretty_print("[+] Starting remote rollback", 'info')

        env.host = host
        env.user = user
        env.port = port
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)
        #	env.use_ssh_config = True

        with cd(remote_dir):
            with settings(warn_only=True):
                if run('test -L previous').failed:
                    pretty_print('Theres nothing to rollback. Returning.', 'info')
                    return
            run('mv current current.prerollback')
            run('mv previous current')


class SrcPreDeploy(Plugin):
    command = 'src_pre_deploy'
    config = None
    description = 'Arguments: None - runs pre_deploy command from config file'

    def validate_config(self):
        if not 'remote' in config:
            raise NotConfiguredError("Remote section does not exists")

        if not 'host' in config['remote'] or not len(config['remote']['host']):
            raise NotConfiguredError("Host not set.")

        if not 'user' in config['remote'] or not len(config['remote']['user']):
            raise NotConfiguredError("User not set.")

        if not 'port' in config['remote']:
            pretty_print("Port not set. Using 22", 'info')
            config['remote']['port'] = 22
        env.port = config['remote']['port']

        if not 'deploy' in config:
            raise NotConfiguredError('No section "deploy" in config.')

        if not 'dir' in config['deploy'] or not len(config['deploy']['dir']):
            config['deploy']['dir'] = 'app'

    def run(self, *args, **kwargs):
        self.validate_config()

        user = config['remote']['user']
        host = config['remote']['host']
        port = config['remote']['port']
        command_list = config['deploy']['pre']

        env.host = host
        env.user = user
        env.port = port

        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        pretty_print("[+] Starting remote pre-deploy commands", 'info')

        if not len(command_list):
            pretty_print('Pre_deploy commands not provided', 'info')
            return

        SrcRemoteCheck(config).run()

        for i in command_list:
            run(i)

        pretty_print("[+] Remote pre-deploy command finished", 'info')


class SrcPostDeploy(Plugin):
    command = 'src_post_deploy'
    config = None
    description = 'Arguments: None - runs post_deploy command from config file'

    def validate_config(self):
        if not 'remote' in config:
            raise NotConfiguredError("Remote section does not exists")

        if not 'host' in config['remote'] or not len(config['remote']['host']):
            raise NotConfiguredError("Host not set.")

        if not 'user' in config['remote'] or not len(config['remote']['user']):
            raise NotConfiguredError("User not set.")

        if not 'port' in config['remote']:
            pretty_print("Port not set. Using 22", 'info')
            config['remote']['port'] = 22
        env.port = config['remote']['port']

        if not 'deploy' in config:
            raise NotConfiguredError('No section "deploy" in config.')

        if not 'dir' in config['deploy'] or not len(config['deploy']['dir']):
            config['deploy']['dir'] = 'app'

    def run(self, *args, **kwargs):
        self.validate_config()

        user = config['remote']['user']
        host = config['remote']['host']
        port = config['remote']['port']
        command_list = config['deploy']['post']

        env.host = host
        env.user = user
        env.port = port

        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        pretty_print("[+] Starting remote post-deploy commands", 'info')

        if not len(command_list):
            pretty_print('Post_deploy commands not provided', 'info')
            return

        SrcRemoteCheck(config).run()

        for i in command_list:
            run(i)

        pretty_print("[+] Remote post-deploy command finished", 'info')


class SrcRemoteVenv(Plugin):
    command = 'src_remote_venv'
    config = None
    description = 'Arguments: None - check if venv exists, if not it will be created, and populated with ' \
                  'requirements.txt'

    def validate_config(self):
        if not 'remote' in config:
            raise NotConfiguredError("Remote section does not exists")

        if not 'host' in config['remote'] or not len(config['remote']['host']):
            raise NotConfiguredError("Host not set.")

        if not 'user' in config['remote'] or not len(config['remote']['user']):
            raise NotConfiguredError("User not set.")

        if not 'port' in config['remote']:
            pretty_print("Port not set. Using 22", 'info')
            config['remote']['port'] = 22
        env.port = config['remote']['port']

        if not 'venv' in config:
            raise NotConfiguredError('No section "venv" in config.')

        if not 'dir' in config['venv'] or not len(config['venv']['dir']):
            config['venv']['dir'] = ""

    def run(self, *args, **kwargs):
        self.validate_config()

        check = kwargs.get('check', True)
        install = kwargs.get('install', True)

        user = config['remote']['user']
        host = config['remote']['host']
        port = config['remote']['port']

        venv_dir = config['venv']['dir']
        update = config['venv']['update']
        requirements_files = config['venv']['requirements']

        deploy_dir = config['deploy']['dir']

        if not len(venv_dir):
            pretty_print('[-] Venv dir not set. Returning.')
            return

        update_str = ""
        if update:
            update_str = "U"

        env.host = host
        env.user = user
        env.port = port

        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        pretty_print("[+] Starting remote venv check", 'info')

        SrcRemoteCheck(config).run()
        pretty_print(venv_dir)
        if check:
            if not files.exists(venv_dir):
                pretty_print("[+] Venv not exits, creating", 'info')

                run('virtualenv {} -p /usr/bin/python2'.format(venv_dir))
            else:
                pretty_print("[+] Venv already exists.", 'info')

        if install:
            with source_virtualenv():
                for req_file in requirements_files:
                    req_file = os.path.join(deploy_dir, 'current', req_file)
                    if files.exists("%s" % os.path.join(req_file)):
                        run('pip install -r%s %s' % (update_str, req_file))

        pretty_print("[+] Remote venv check finished", 'info')


class Deploy(Plugin):
    command = 'deploy'
    config = None
    description = 'Arguments: <local_subfolder> - deploys new version'

    def validate_config(self):
        return True

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            subdir = args[0]
        except IndexError:
            subdir = ''

        pretty_print("[+] Starting deployment.", 'info')

        if not config:
            raise NotConfiguredError('Deploy - config not provided')

        date = datetime.now().strftime("%Y%m%d_%H%M%S")

        steps = [SrcRemoteCheck, SrcPreDeploy, SrcClone, SrcPrepare, SrcUpload, SrcRemoteExtract,
                 SrcRemoteDeploy, SrcRemoteConfig, SrcPostDeploy]

        SrcRemoteVenv(config).run(install=False)

        for step in steps:
            if step in [SrcRemoteExtract, SrcRemoteDeploy]:
                step(config).run(date)
            else:
                step(config).run()

        SrcRemoteVenv(config).run(check=False)

        pretty_print('Cleaning flag: %s' % config['remote']['clean'])
        if config['remote']['clean']:
            clean = SrcClean(config)
            clean.run(config['source']['file'])
            clean.run(date)
        else:
            pretty_print('Cleaning not selected, omitting.', 'info')
        pretty_print("[+] Deployment finished.", 'info')