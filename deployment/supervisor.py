#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

from __future__ import print_function

import xmlrpclib

from misc import *


def validate_config(config_f):
	config = prepare_config(config_f, 'Restart')

	pretty_print("Validating restart config section", 'debug')

	#SUPERVISOR_ADDRESS, SUPERVISOR_PORT, SUPERVISOR_PASSWORD, SUPERVISOR_APP_NAME
	validate_entry(config, 'supervisor_host', required=True, default=None)
	validate_entry(config, 'supervisor_port', required=True, default=None)
	validate_entry(config, 'supervisor_password', required=True, default=None)
	validate_entry(config, 'supervisor_app_name', required=True, default=None)
	validate_entry(config, 'supervisor_user', required=True, default=None)

	pretty_print('Config is valid!', 'debug')

	return config

def restart_supervisor(config_f):
	config = validate_config(config_f)

	env.host_string = 'localhost'
	pretty_print('[+] Supervisor restart procedure start', 'info')

	server = xmlrpclib.Server('http://%s:%s@%s:%s/RPC2' % (config['supervisor_user'], config['supervisor_password'], config['supervisor_host'], config['supervisor_port']))

	try:
		env.host_string = config['supervisor_host']
		pretty_print("Stopping process: %s" % config['supervisor_app_name'], "info")
		server.supervisor.stopProcess(config['supervisor_app_name'])
		pretty_print("Starting process: %s" % config['supervisor_app_name'], "info")
		server.supervisor.startProcess(config['supervisor_app_name'])
	except xmlrpclib.Fault as ex:
		if ex.faultCode == 70:
			pretty_print("Process not running, lets start him", 'info')
			server.supervisor.startProcess(config['supervisor_app_name'])
		else:
			# pretty_print("Something went wrong: %i - %s" % (ex.faultCode, ex.faultString), 'error')
			raise Exception("Something went wrong: %i - %s" % (ex.faultCode, ex.faultString))
	except xmlrpclib.ProtocolError as prot:
		raise Exception("ProtocolError: %s - %s " % (prot.errcode, prot.errmsg))

	pretty_print('[+] Supervisor restart procedure finished', 'info')
