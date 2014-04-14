#
# Deployment and database migration tool
#
# Copyright (C) 2012-2014 TEONITE
# Copyright (C) 2012-2014 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#
from __future__ import print_function

import xmlrpclib
from fabric.state import env

from deployment.common import NotConfiguredError, pretty_print
from deployment.plugin import Plugin

__author__ = 'kkrzysztofik'


class Supervisor(Plugin):
    command = ['restart_supervisor']
    config = None
    description = 'Arguments: <process_name> <process_name> ... - restart process in Supervisor'

    def validate_config(self):
        #config = prepare_config(config_f, 'Restart')
        pretty_print("Validating supervisor config section", 'debug')

        if not 'supervisor' in self.config:
            raise NotConfiguredError("Supervisor section does not exists")

        supervisor_conf = self.config['supervisor']

        if not 'host' in supervisor_conf or not len(supervisor_conf['host']):
            raise NotConfiguredError("Host not set")

        if not 'port' in supervisor_conf['supervisor']:
            supervisor_conf['port'] = 9001

        if not 'user' in supervisor_conf['supervisor'] or not len(supervisor_conf['user']):
            supervisor_conf['user'] = 'admin'

        if not 'password' in supervisor_conf or not len(supervisor_conf['password']):
            supervisor_conf['password'] = ''

        pretty_print('Config is valid!', 'debug')

    def run(self, **kwargs):
        apps = kwargs.get('apps', None)

        if not apps:
            if not 'apps' in self.config['supervisor']:
                raise NotConfiguredError("Apps not set")

            if not type(self.config['supervisor']['apps']) == type(list()):
                raise Exception("Wrong format of 'apps' section - should be list")

            apps = self.config['supervisor']['apps']

        env.host_string = 'localhost'
        pretty_print('[+] Supervisor restart procedure start', 'info')

        supervisor_conf = self.config['supervisor']
        server = xmlrpclib.Server('http://%s:%s@%s:%i/RPC2' % (
            supervisor_conf['user'], supervisor_conf['password'], supervisor_conf['host'], supervisor_conf['port'])
        )

        env.host_string = "%s:%s" % (supervisor_conf['host'], supervisor_conf['port'])

        for app in apps:
            try:
                pretty_print("Stopping process: %s" % app, "info")
                server.supervisor.stopProcess(app)
                pretty_print("Starting process: %s" % app, "info")
                server.supervisor.startProcess(app)
            except xmlrpclib.Fault as ex:
                if ex.faultCode == 70:
                    pretty_print("Process not running, lets start him", 'info')
                    server.supervisor.startProcess(app)
                else:
                    pretty_print("Something went wrong: %i - %s" % (ex.faultCode, ex.faultString), 'error')
            except xmlrpclib.ProtocolError as prot:
                raise Exception("ProtocolError: %s - %s " % (prot.errcode, prot.errmsg))

        pretty_print('[+] Supervisor restart procedure finished', 'info')