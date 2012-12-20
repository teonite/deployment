#!/usr/bin/env python
from __future__ import print_function
import getopt

import sys
from fabric.state import env

from deployment.misc import *
from deployment.mysql import *
from deployment.src import *
env.host_string = 'localhost'

def usage():
	_pretty_print('Parameters:')
	_pretty_print(' -c, --config <filename> - if not selected, config.ini is selected')
	_pretty_print('Usage:')
	_pretty_print(' - deploy - deploys new version')
	_pretty_print(' - db_migrate - migrate database to new version')
	_pretty_print(' - src_clone - clone repo to local folder')
	_pretty_print(' - src_prepare - archive repo to file')
	_pretty_print(' - src_upload - upload packed file to remote host')
	_pretty_print(' - src_remote_test - test remote host')
	_pretty_print(' - src_remote_extract - extract uploaded file')
	_pretty_print(' - src_remote_config - copy config from current to extract_dir')
	_pretty_print(' - src_remote_deploy - deploys new version')
	_pretty_print(' - src_remote_rollback - backs to previous version')
	_pretty_print(' - mysql_db_clone - clone db: <db_name> -> <db_name>_<current_date>_<current_time>')
	_pretty_print(' - mysql_db_migrate - runs .sql files from selected folder')
	_pretty_print(' - mysql_db_dump - dump database to selected file')
	_pretty_print(' - mysql_db_restore - restore database from file')

if __name__ == "__main__":
	if len(sys.argv) == 1:
		usage()
		sys.exit()

	try:
		opts, args = getopt.getopt(sys.argv[2:], "c:", ["config="])
	except getopt.GetoptError as err:
		# print help information and exit:
		_pretty_print(str(err)) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	config_f = None
	for o, a in opts:
		if o == "-c" or o == "--config":
			config_f = a
		else:
			_pretty_print("unhandled option")

	try:
		s = sys.argv[1]
		if s == 'deploy':
			deploy(config_f)
		elif s == 'db_migrate':
			db_migrate(config_f)
		elif s == 'src_clone':
			src_clone(config_f)
		elif s == 'src_prepare':
			src_prepare(config_f)
		elif s == 'src_upload':
			src_upload(config_f)
		elif s == 'src_remote_test':
			src_remote_test(config_f)
		elif s == 'src_remote_extract':
			src_remote_extract(config_f)
		elif s == 'src_remote_config':
			src_remote_config(config_f)
		elif s == 'src_remote_deploy':
			src_remote_deploy(config_f)
		elif s == 'src_remote_rollback':
			src_remote_rollback(config_f)
		elif s == 'mysql_db_clone':
			mysql_db_clone(config_f)
		elif s == 'mysql_db_migrate':
			mysql_db_migrate(config_f)
		elif s == 'mysql_db_dump':
			mysql_db_dump(config_f)
		elif s == 'mysql_db_restore':
			mysql_db_restore(config_f)
		else:
			usage()
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		_pretty_print("Something went wrong. Message: %s - %s" % (exceptionType, exceptionValue))
