"""
Example usage

If you want to overwrite settings from localsettings.FABRIC_OPTS:

fab install:hosts="localhost",user=sensexp,dir=/srv/sensexp,confdir=conf

Options that were not specified will be taken from localsettings.FABRIC_OPTS
"""

from __future__ import print_function

import os
import sys
from os.path import dirname, abspath
import re

sys.path.append(dirname(dirname(abspath(__file__))))

from conf.settings import PROJECT_NAME, VERSION, FOOTER_TEMPLATE_DIR
from conf.localsettings import FABRIC_OPTS
from fabric.context_managers import cd, prefix
from fabric.state import env
from fabric.api import run
from fabric.contrib import files

env.use_ssh_config = True
env.dir = 'current'
env.hosts = FABRIC_OPTS['hosts']
env.user = FABRIC_OPTS['user']

def _pretty_print(str):
    print('[%s] INFO: %s' % (env.host, str))
    
def _parse_args(user, dir, repo, confdir):
    PARSED_OPTS = {}

    PARSED_OPTS['user'] = user if user else FABRIC_OPTS['user']
    PARSED_OPTS['dir'] = dir if dir else FABRIC_OPTS['dir']
    PARSED_OPTS['repo'] = repo if repo else FABRIC_OPTS['repo']
    PARSED_OPTS['confdir'] = confdir if confdir else FABRIC_OPTS['confdir']
    
    env.user = PARSED_OPTS['user']
    
    return PARSED_OPTS
    
def _prefix(fabric_opts):
    return 'source %s' % os.path.join('~', fabric_opts['dir'], 'sensexp_env/bin/activate')
    
def install(user=None, dir=None, repo=None, confdir=None):
    _pretty_print('[+] Starting install.')
    OPTS = _parse_args(user, dir, repo, confdir)
    run('test -d %s || mkdir %s' % (OPTS['dir'], OPTS['dir']))
    with cd(OPTS['dir']):
        _pretty_print('Creating virtual environment.')
        run('virtualenv sensexp_env')
        with prefix(_prefix(OPTS)):
            _pretty_print('Cloning from remote repo: %s' % (OPTS['repo']))
            run('git clone %s' % (OPTS['repo']))
            with cd(PROJECT_NAME):
                _pretty_print('Installing requirements')
                run('pip install -r src/requirements.txt')
    _pretty_print("[+] Install done. Remember to deploy an application.")


class NotConfiguredError(Exception):
    pass

def deploy(user=None, dir=None, repo=None, confdir=None):
    _pretty_print('[+] Starting deployment')
    OPTS = _parse_args(user, dir, repo, confdir)
    with prefix(_prefix(OPTS)):
        with cd(os.path.join(OPTS['dir'], PROJECT_NAME)):
            _pretty_print('Pulling git repository to last revision')
            run('git pull origin master')
            try:
                _check_config(OPTS['confdir'])
            except NotConfiguredError:
                _pretty_print(
                    '[!] You need to configure files in %s folder and then run dbsync' % os.path.join(OPTS['dir'],
                        PROJECT_NAME, env.dir, 'settings'))
                return
            
            _update_footer()

    _pretty_print('[+] Finished deployment')

def _update_footer():
    # Update version and revision in footer
    _pretty_print('[+] Updating footer with version and revision no')
    run('python src/tools/update_version.py')

def _check_config(confdir):
    _pretty_print('[+] Checking application configuration')
    if not files.exists('src/%s/localsettings.py' % confdir):
        _pretty_print('Missing config file: localsettings.py')

def _upgrade():
    _pretty_print('[+] Updating required packages')
    run('pip install --upgrade -r requirements.txt')
    _pretty_print('[+] Requirements upgrade done.')


def upgrade(user=None, dir=None, repo=None, confdir=None):
    OPTS = _parse_args(user, dir, repo, confdir)
    with prefix(_prefix(OPTS)):
        with cd(os.path.join(OPTS['dir'], PROJECT_NAME, 'src')):
            _upgrade()


def _dbsync():
    _pretty_print('[+] Synchronizing database')
    run('mv local.db local.db.old')
    run('./tools/manage.py syncdb')
    # TODO: South migration


def dbsync(user=None, dir=None, repo=None, confdir=None):
    OPTS = _parse_args(user, dir, repo, confdir)
    with prefix(_prefix(OPTS)):
        with cd(os.path.join(OPTS['dir'], PROJECT_NAME, 'src')):
            _dbsync()

def usage():
    _pretty_print('install - create environment, git clone and install requirements')
    _pretty_print('deploy - git pull, copy src to right place, upgrade requirements and dbsync')
    _pretty_print('upgrade - upgrade requirements')
    _pretty_print('dbsync - synchronize database and migrations')

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
