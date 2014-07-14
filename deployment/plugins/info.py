#
# Deployment and database migration tool
#
# Copyright (C) 2012-2014 TEONITE
# Copyright (C) 2012-2014 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

from __future__ import print_function

import time

from git import Repo, InvalidGitRepositoryError

from deployment.libs.prepender import Prepender
from deployment.libs.mail import send_mail

from deployment import defaults
from deployment.common import *
from deployment.plugin import Plugin

__author__ = 'kkrzysztofik'


class WriteCommitInfo(Plugin):
    command = 'commit_info'
    config = None
    description = 'Arguments: <none> - write to changelog file info about commit since last build'

    def validate_config(self):
        pass

    def run(self, *args, **kwargs):
        changelog_filename = config['deploy']['changelog']
        all_commits = config['deploy']['all_commits']
        local_directory = config['source']['local']
        repo_directory = config['source']['git']['local']
        branch = config['source']['git']['branch']

        env.host_string = 'localhost'
        pretty_print('[+] Write commit info start', 'info')

        if not len(changelog_filename):
            pretty_print("No changelog file provided, returning", 'info')
            return

        old_dir = os.getcwd()
        os.chdir(local_directory)

        try:
            with open("previous_build", "r") as build_file:
                last_build = build_file.readline().strip()
        except IOError:
            try:
                last_build = os.environ['GIT_PREVIOUS_COMMIT']
            except KeyError:
                last_build = None

        try:
            repo = Repo(repo_directory)
            pretty_print('Repository found.', 'info')
        except InvalidGitRepositoryError:  # Repo doesn't exists
            raise NotConfiguredError('Repository not found. Please provide correct one.')

        if not len(branch):
            branch = repo.active_branch

        if repo.active_branch is not branch:
            pretty_print('Changing branch', 'info')
            repo.git.checkout('master')

        pretty_print('Pulling changes', 'info')
        repo.git.pull('origin', branch)

        last_commit = repo.head.commit

        if not all_commits:
            mode = "a"
            if last_build:
                commits = "%s..HEAD" % last_build
            else:
                commits = "-n1"
        else:
            mode = "w"
            commits = None

        with Prepender(os.path.join(local_directory, repo_directory, changelog_filename), mode) as changelog_file:
            head_str = u'%s, %s - %s <%s>\n' % (last_commit.hexsha[:8],
                                                time.strftime(u"%a, %d %b %Y %H:%M", time.gmtime(last_commit.committed_date)),
                                                last_commit.committer.name, last_commit.committer.email)

            if commits:
                gitlog = repo.git.log(commits, u'--format=* [%h] - %s')
            else:
                gitlog = repo.git.log(u'--format=* [%h] - %s')

            if len(gitlog):
                write_str = head_str + u"%s\n\n" % (u"#" * len(head_str)) + gitlog + u"\n\n"
                changelog_file.write(write_str)

        # compression = file.split('.')
        pretty_print("cwd: %s" % os.getcwd())

        if not all_commits:
            with open("previous_build", "w") as build_file:
                build_file.write(last_commit.hexsha)

        os.chdir(old_dir)
        pretty_print('[+] Write commit info finished', 'info')


class NotifyMail(Plugin):
    command = 'notify'
    config = None
    description = 'Arguments: <none> - send mail with deploy notification'

    def validate_config(self):
        if not len(config['mail']['project_name']):
            raise NotConfiguredError("Project name not set.")

        if not len(config['mail']['from_mail']):
            raise NotConfiguredError("From: mail not set.")

        if not len(config['mail']["people"]):
            raise NotConfiguredError("No people to notify")

    def run(self, *args, **kwargs):
        self.validate_config()

        project_name = config['mail']['project_name']
        from_mail = config['mail']['from_mail']
        people = config['mail']["people"]
        host = config['mail']['server']['host']
        user = config['mail']['server']['user']
        password = config['mail']['server']['password']
        port = config['mail']['server']['port']
        local_dir = config['source']['local']
        repo_dir = config['source']['git']['local']

        template_path = os.path.join(local_dir, repo_dir, config['mail']['template_path'])

        env.host_string = 'localhost'
        pretty_print('[+] Notify mail start', 'info')

        if not len(template_path):
            subject = defaults.SUBJECT_TEMPLATE.format(project_name=project_name)
            message = defaults.MESSAGE_TEMPLATE.format(project_name=project_name)
        else:
            template_path = os.path.expanduser(template_path)
            head, tail = os.path.split(template_path)

            if tail.endswith(".py"):
                tail = tail[:-3]
            else:
                raise NotConfiguredError("Template file must be .py file")

            sys.path.insert(0, head)
            templates = __import__(tail)

            subject = templates.SUBJECT_TEMPLATE.format(project_name=project_name)
            message = templates.MESSAGE_TEMPLATE.format(project_name=project_name)

        message = "".join([message, "\n\n--\nSent automatically by TEONITE Deployment (http://teonite.com)\nCopyright (C) TEONITE (http://teonite.com)"])
        send_mail(from_mail, people, subject, message, host=host, user=user, password=password, port=port)

        pretty_print('[+] Notify mail finished', 'info')
