#
# Deployment, provisioning and database migration tool
#
# Copyright (C) 2012-2014 TEONITE
# Copyright (C) 2012-2014 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

from __future__ import print_function

import os
import sys
import logging
import logging.config
import json
import traceback
from collections import Mapping

from fabric.state import env
from fabric.api import run
from fabric.context_managers import contextmanager, prefix

import defaults

_log = None
log = None
config = None


def _setupLogging(config):
    """
    Setup logging
    """
    global _log
    logging.config.dictConfig(config)
    _log = logging


def getLogger(config):
    """
    Get configured logger
    """

    if _log is None:
        if not 'logger' in config:
            _setupLogging(defaults.LOGGING)
        else:
            _setupLogging(config['logger'])

    return logging.getLogger('deployment')


def prepare_logger(config):
    global log
    log = getLogger(config)


def logException(ex):
    log.debug("Error while saving form..")
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    log.error("exception caught while saving form, here's the trace: '%s'",
              repr(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback))
    )


class NotConfiguredError(Exception):
    pass


def pretty_print(msg, level='debug'):
    if not log:
        print('[%s] ERROR: %s' % (env.host_string, "logger not configured"))
        print('[%s] ERROR: %s' % (env.host_string, msg))
    else:
        if level == 'debug':
            log.debug('[\x1b[36m%s\x1b[0m] \x1b[35mDEBUG\x1b[0m: %s' % (env.host_string, msg))
        elif level == 'info':
            log.info('[\x1b[36m%s\x1b[0m] \x1b[32mINFO\x1b[0m: %s' % (env.host_string, msg))
        elif level == 'error':
            log.error('[\x1b[36m%s\x1b[0m] \x1b[31mERROR\x1b[0m: %s' % (env.host_string, msg))
        elif level == 'warning':
            log.warning('[\x1b[36m%s\x1b[0m] \x1b[33mWARNING\x1b[0m: %s' % (env.host_string, msg))


def _parse_config(filename):
    #pretty_print("Parsing config file: %s" % filename, 'debug')
    try:
        f = open(filename, 'r')
        conf = json.load(f)
        # pretty_print(conf[section], 'debug')

        return conf

    except IOError:
        # exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # print("Something went wrong. Returning empty map. Message: %s - %s" % (exceptionType, exceptionValue))
        return {}


def update(d, u, depth=-1):
    """
    Recursively merge or update dict-like objects.
    >>> update({'k1': {'k2': 2}}, {'k1': {'k2': {'k3': 3}}, 'k4': 4})
    {'k1': {'k2': {'k3': 3}}, 'k4': 4}
    """

    for k, v in u.iteritems():
        if isinstance(v, Mapping) and not depth == 0:
            r = update(d.get(k, {}), v, depth=max(depth - 1, -1))
            d[k] = r
        elif isinstance(d, Mapping):
            d[k] = u[k]
        else:
            d = {k: u[k]}
    return d


def prepare_config(config_f=None, remote_tuple=(None, None, None)):
    global config

    if not config:
        if not config_f:
            config = _parse_config("config.json")
        else:
            config = _parse_config(config_f)

    config = update(defaults.config, config)

    if remote_tuple[0]:
        config['remote']['user'] = remote_tuple[0]
    if remote_tuple[1]:
        config['remote']['host'] = remote_tuple[1]
    if remote_tuple[2]:
        config['remote']['port'] = remote_tuple[2]

    return config


def list_dir(dir_=None):
    """returns a list of files in a directory (dir_) as absolute paths"""
    #dir_ = dir_ or env.cwd
    string_ = run("for i in *; do echo $i; done")
    files = string_.replace("\r", "").split("\n")
    return files


def parse_remote(remote_str):
    user = None
    host = None
    port = None

    if "@" in remote_str:
        remote_split = remote_str.rsplit("@", 1)
        user = remote_split[0]
        host = remote_split[1]

        if ":" in user:
            user = user.split(":", 1)[0]
        if ":" in host:
            host_split = host.rsplit(":", 1)

            host = host_split[0]
            port = host_split[1]
    else:
        host = remote_str

        if ":" in host:
            host_split = host.rsplit(":", 1)

            host = host_split[0]
            port = host_split[1]

    return user, host, port


@contextmanager
def source_virtualenv():
    with prefix('source ' + os.path.join(config['venv']['dir'], 'bin/activate')):
        yield
