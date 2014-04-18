#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#
from __future__ import print_function

import sys
import logging
import logging.config
import json
import traceback

from fabric.state import env
from fabric.api import run

import defaults

LOGGING = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(levelname)s %(message)s"
        },
        "verbose": {
            "format": "[%(asctime)s] \"%(message)s\"",
            "datefmt": "%d/%b/%Y %H:%M:%S"
        }
    },

    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": "ext://sys.stdout"
        },
        "graypy": {
            "level": "INFO",
            "class": "graypy.GELFHandler",
            "formatter": "verbose",
            "host": "logs.teonite.net",
            "port": 12201
        }
    },

    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": "DEBUG"
        },
        "deployment": {
            "handlers": ["console"],
            "level": "DEBUG",
            "qualname": "deployment",
            "propagate": False
        }
    }
}

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
            _setupLogging(LOGGING)
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


def _parse_config(filename, section=None):
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


def prepare_config(config_f=None):
    global config
    try:
        if not config:
            if not config_f:
                config = _parse_config("config.json")
            else:
                config = _parse_config(config_f)
        defaults.config.update(config)
        config = defaults.config
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))
        pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))

    return config


def list_dir(dir_=None):
    """returns a list of files in a directory (dir_) as absolute paths"""
    #dir_ = dir_ or env.cwd
    string_ = run("for i in *; do echo $i; done")
    files = string_.replace("\r", "").split("\n")
    return files