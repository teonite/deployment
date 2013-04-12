#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

from __future__ import print_function

import xmlrpclib

from misc import *


def validate_config(config):
	#config = prepare_config(config_f, 'Restart')

	pretty_print("Validating supervisor config section", 'debug')

	if not 'supervisor' in config:
		raise NotConfiguredError("Supervisor section does not exists")

	if not 'host' in config['supervisor'] or not len(config['supervisor']['host']):
		raise NotConfiguredError("Host not set")

	if not 'port' in config['supervisor']:
		raise NotConfiguredError("Port not set")

	if not 'user' in config['supervisor'] or not len(config['supervisor']['user']):
		raise NotConfiguredError("User not set")

	if not 'password' in config['supervisor'] or not len(config['supervisor']['password']):
		raise NotConfiguredError("Password not set")

	pretty_print('Config is valid!', 'debug')

	return config

def restart_supervisor(config_f, apps=None):
	config = prepare_config(config_f)
	config = validate_config(config)

	if not apps:
		if not 'apps' in config['supervisor']:
			raise NotConfiguredError("Apps not set")

		if not type(config['supervisor']['apps']) == type(list()):
			raise Exception("Wrong format of 'apps' section - should be list")

		apps = config['supervisor']['apps']

	env.host_string = 'localhost'
	pretty_print('[+] Supervisor restart procedure start', 'info')

	server = xmlrpclib.Server('http://%s:%s@%s:%i/RPC2' % (config['supervisor']['user'], config['supervisor']['password'], config['supervisor']['host'], config['supervisor']['port']))

	env.host_string = config['supervisor']['host']
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
