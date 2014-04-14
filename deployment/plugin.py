#
# Deployment and database migration tool
#
# Copyright (C) 2012-2014 TEONITE
# Copyright (C) 2012-2014 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#
__author__ = 'kkrzysztofik'

import os
import sys


class Plugin(object):
    command = None
    config = None
    description = None

    def __init__(self, config, **kwargs):
        self.config = config

    def validate_config(self):
        raise NotImplementedError()

    def run(self, **kwargs):
        raise NotImplementedError()


def init_plugins():
    find_plugins()
    register_plugins()


def find_plugins():
    """
        find all files in the plugin directory and imports them
    """
    plugin_dir = os.path.realpath("plugins")
    plugin_files = [x[:-3] for x in os.listdir(plugin_dir) if x.endswith(".py")]
    sys.path.insert(0, plugin_dir)

    for plugin in plugin_files:
        mod = __import__(plugin)


def register_plugins():
    """
        Register all class based plugins.

        Uses the fact that a class knows about all of its subclasses
        to automatically initialize the relevant plugins
    """
    plugins = []

    for plugin in Plugin.__subclasses__():
        plugins[plugin.command] = plugin

    return plugins