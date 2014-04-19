#
# Deployment and database migration tool
#
# Copyright (C) 2012 TEONITE
# Copyright (C) 2012 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

from __future__ import print_function

import sys
import os
from datetime import datetime

from fabric.context_managers import cd, hide
from fabric.operations import put
from fabric.state import env
from fabric.api import run
from fabric.contrib import files

from deployment.common import *
from deployment.plugin import Plugin


class MySQLDumpRemove(Plugin):
    command = 'mysql_dump_remove'
    config = None
    description = 'Arguments: None - remove dump file from remote host'

    def validate_config(self):
        if not 'shell' in config['mysql']:
            raise NotConfiguredError("shell section does not exists")

        if not 'host' in config['mysql']['shell'] or not len(config['mysql']['shell']['host']):
            raise NotConfiguredError("host not set")
        if not 'user' in config['mysql']['shell'] or not len(config['mysql']['shell']['user']):
            raise NotConfiguredError("user not set")
        if not 'port' in config['mysql']['shell'] or not (type(config['mysql']['shell']['port']) == type(int)):
            pretty_print("port not set, using default one", "info")
            config['mysql']['shell']['port'] = 22
            env.port = config['mysql']['shell']['port']

        if not 'dumpfile' in config['mysql']['shell'] or not len(config['mysql']['shell']['dumpfile']):
            pretty_print("migration_dir not set, using default: dump.sql")
            config['mysql']['shell']['migration_dir'] = "dump.sql"

    def run(self, *args, **kwargs):
        self.validate_config()

        user = config['mysql']['shell']['user']
        host = config['mysql']['shell']['host']
        port = config['mysql']['shell']['port']
        filename = config['mysql']['shell']['dumpfile']

        env.host = host
        env.user = user
        env.port = port
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        pretty_print("[+] Starting dump remove.", 'info')

        if files.exists(filename):
            pretty_print('File %s found. Removing.' % filename)
            run('rm %s' % filename)
        else:
            raise Exception('Dump file not found.')

        pretty_print("[+] Dump remove finished.", 'info')


class MySQLDBDump(Plugin):
    command = 'mysql_db_dump'
    config = None
    description = 'Arguments: <database> - dump database to selected file'

    def validate_config(self):
        if not 'server' in config['mysql']:
            raise NotConfiguredError("server section does not exists")

        if not 'host' in config['mysql']['server'] or not len(config['mysql']['server']['host']):
            raise NotConfiguredError("host not set")
        if not 'user' in config['mysql']['server'] or not len(config['mysql']['server']['user']):
            raise NotConfiguredError("user not set")
        if not 'password' in config['mysql']['server'] or not len(config['mysql']['server']['password']):
            raise NotConfiguredError("password not set")
        if not 'port' in config['mysql']['server'] or not (type(config['mysql']['server']['port']) == type(int)):
            pretty_print("port not set, using default one", "info")
            config['mysql']['server']['port'] = 3306
        if not 'database' in config['mysql']['server'] or not len(config['mysql']['server']['database']):
            raise NotConfiguredError("database not set")

        if not 'shell' in config['mysql']:
            raise NotConfiguredError("shell section does not exists")

        if not 'host' in config['mysql']['shell'] or not len(config['mysql']['shell']['host']):
            raise NotConfiguredError("host not set")
        if not 'user' in config['mysql']['shell'] or not len(config['mysql']['shell']['user']):
            raise NotConfiguredError("user not set")
        if not 'port' in config['mysql']['shell'] or not (type(config['mysql']['shell']['port']) == type(int)):
            pretty_print("port not set, using default one", "info")
            config['mysql']['shell']['port'] = 22
            env.port = config['mysql']['shell']['port']

        if not 'dumpfile' in config['mysql']['shell'] or not len(config['mysql']['shell']['dumpfile']):
            pretty_print("migration_dir not set, using default: dump.sql")
            config['mysql']['shell']['migration_dir'] = "dump.sql"

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            database = args[0]
        except IndexError:
            database = config['mysql']['server']['database']

        user = config['mysql']['shell']['user']
        host = config['mysql']['shell']['host']
        port = config['mysql']['shell']['port']
        filename = config['mysql']['shell']['dumpfile']

        dbhost = config['mysql']['server']['host']
        dbuser = config['mysql']['server']['user']
        dbpassword = config['mysql']['server']['password']

        env.host = host
        env.user = user
        env.port = port
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        pretty_print('[+] Starting MySQL dump.', 'info')

        with hide('running'):
            pretty_print('Running mysqldump.', 'info')
            run('mysqldump -u%s -p%s -h%s %s > %s' % (dbuser, dbpassword, dbhost, database, filename))
        pretty_print('[+] MySQL dump finished.', 'info')


class MySQLDBRestore(Plugin):
    command = 'mysql_db_restore'
    config = None
    description = 'Arguments: <database> - restore database from file'

    def validate_config(self):
        if not 'server' in config['mysql']:
            raise NotConfiguredError("server section does not exists")

        if not 'host' in config['mysql']['server'] or not len(config['mysql']['server']['host']):
            raise NotConfiguredError("host not set")
        if not 'user' in config['mysql']['server'] or not len(config['mysql']['server']['user']):
            raise NotConfiguredError("user not set")
        if not 'password' in config['mysql']['server'] or not len(config['mysql']['server']['password']):
            raise NotConfiguredError("password not set")
        if not 'port' in config['mysql']['server'] or not (type(config['mysql']['server']['port']) == type(int)):
            pretty_print("port not set, using default one", "info")
            config['mysql']['server']['port'] = 3306
        if not 'database' in config['mysql']['server'] or not len(config['mysql']['server']['database']):
            raise NotConfiguredError("database not set")

        if not 'shell' in config['mysql']:
            raise NotConfiguredError("shell section does not exists")

        if not 'host' in config['mysql']['shell'] or not len(config['mysql']['shell']['host']):
            raise NotConfiguredError("host not set")
        if not 'user' in config['mysql']['shell'] or not len(config['mysql']['shell']['user']):
            raise NotConfiguredError("user not set")
        if not 'port' in config['mysql']['shell'] or not (type(config['mysql']['shell']['port']) == type(int)):
            pretty_print("port not set, using default one", "info")
            config['mysql']['shell']['port'] = 22
            env.port = config['mysql']['shell']['port']

        if not 'dumpfile' in config['mysql']['shell'] or not len(config['mysql']['shell']['dumpfile']):
            pretty_print("migration_dir not set, using default: dump.sql")
            config['mysql']['shell']['migration_dir'] = "dump.sql"

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            database = args[0]
        except IndexError:
            database = config['mysql']['server']['database']

        user = config['mysql']['shell']['user']
        host = config['mysql']['shell']['host']
        port = config['mysql']['shell']['port']
        filename = config['mysql']['shell']['dumpfile']
        dbhost = config['mysql']['server']['host']
        dbuser = config['mysql']['server']['user']
        dbpassword = config['mysql']['server']['password']

        env.host = host
        env.user = user
        env.port = port
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        pretty_print('[+] Starting MySQL restore.', 'info')

        #	env.use_ssh_config = True
        with hide('running'):
            pretty_print('Restoring to %s from %s' % (database, filename), 'info')
            run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, filename))
        pretty_print('[+] MySQL restore finished.', 'info')


class MySQLDBClone(Plugin):
    command = 'mysql_db_clone'
    config = None
    description = 'Arguments: <db_name> - clone db: <db_name> -> <db_name>_<current_date>_<current_time>'

    def validate_config(self):
        if not 'server' in config['mysql']:
            raise NotConfiguredError("server section does not exists")

        if not 'host' in config['mysql']['server'] or not len(config['mysql']['server']['host']):
            raise NotConfiguredError("host not set")
        if not 'user' in config['mysql']['server'] or not len(config['mysql']['server']['user']):
            raise NotConfiguredError("user not set")
        if not 'password' in config['mysql']['server'] or not len(config['mysql']['server']['password']):
            raise NotConfiguredError("password not set")
        if not 'port' in config['mysql']['server'] or not (type(config['mysql']['server']['port']) == type(int)):
            pretty_print("port not set, using default one", "info")
            config['mysql']['server']['port'] = 3306
        if not 'database' in config['mysql']['server'] or not len(config['mysql']['server']['database']):
            raise NotConfiguredError("database not set")

        if not 'shell' in config['mysql']:
            raise NotConfiguredError("shell section does not exists")

        if not 'host' in config['mysql']['shell'] or not len(config['mysql']['shell']['host']):
            raise NotConfiguredError("host not set")
        if not 'user' in config['mysql']['shell'] or not len(config['mysql']['shell']['user']):
            raise NotConfiguredError("user not set")
        if not 'port' in config['mysql']['shell'] or not (type(config['mysql']['shell']['port']) == type(int)):
            pretty_print("port not set, using default one", "info")
            config['mysql']['shell']['port'] = 22
            env.port = config['mysql']['shell']['port']

        if not 'dumpfile' in config['mysql']['shell'] or not len(config['mysql']['shell']['dumpfile']):
            pretty_print("migration_dir not set, using default: dump.sql")
            config['mysql']['shell']['migration_dir'] = "dump.sql"

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            database = args[0]
        except IndexError:
            database = config['mysql']['server']['database']

        user = config['mysql']['shell']['user']
        host = config['mysql']['shell']['host']
        port = config['mysql']['shell']['port']
        dbhost = config['mysql']['server']['host']
        dbuser = config['mysql']['server']['user']
        dbpassword = config['mysql']['server']['password']

        env.host = host
        env.user = user
        env.port = port
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        pretty_print('[+] Starting MySQL clone.', 'info')

        new_database = '%s_%s' % (database, datetime.now().strftime("%Y%m%d_%H%M%S"))

        with hide('running'):
            MySQLDBDump(config).run(database)

            pretty_print('Creating new database: %s' % new_database)
            run('mysql -u%s -p%s -h%s %s <<< %s' % (dbuser, dbpassword, dbhost, database,
                                                    '\"CREATE DATABASE %s\"' % new_database))
            MySQLDBRestore(config).run(new_database)

        pretty_print('[+] MySQL clone finished.', 'info')


class MySQLDBMigrate(Plugin):
    command = 'mysql_db_migrate'
    config = None
    description = 'Arguments: <migration_folder> - runs .sql files from selected folder'

    def validate_config(self):
        if not 'server' in config['mysql']:
            raise NotConfiguredError("server section does not exists")

        if not 'host' in config['mysql']['server'] or not len(config['mysql']['server']['host']):
            raise NotConfiguredError("host not set")
        if not 'user' in config['mysql']['server'] or not len(config['mysql']['server']['user']):
            raise NotConfiguredError("user not set")
        if not 'password' in config['mysql']['server'] or not len(config['mysql']['server']['password']):
            raise NotConfiguredError("password not set")
        if not 'port' in config['mysql']['server'] or not (type(config['mysql']['server']['port']) == type(int)):
            pretty_print("port not set, using default one", "info")
            config['mysql']['server']['port'] = 3306
        if not 'database' in config['mysql']['server'] or not len(config['mysql']['server']['database']):
            raise NotConfiguredError("database not set")

        if not 'shell' in config['mysql']:
            raise NotConfiguredError("shell section does not exists")

        if not 'host' in config['mysql']['shell'] or not len(config['mysql']['shell']['host']):
            raise NotConfiguredError("host not set")
        if not 'user' in config['mysql']['shell'] or not len(config['mysql']['shell']['user']):
            raise NotConfiguredError("user not set")
        if not 'port' in config['mysql']['shell'] or not (type(config['mysql']['shell']['port']) == type(int)):
            pretty_print("port not set, using default one", "info")
            config['mysql']['shell']['port'] = 22
            env.port = config['mysql']['shell']['port']

        if not 'dumpfile' in config['mysql']['shell'] or not len(config['mysql']['shell']['dumpfile']):
            pretty_print("migration_dir not set, using default: dump.sql")
            config['mysql']['shell']['migration_dir'] = "dump.sql"

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            local_dir = args[0]
        except IndexError:
            raise NotConfiguredError("Please provide local migration dir")

        remote_dir = config['mysql']['shell']['migration_dir']
        user = config['mysql']['shell']['user']
        host = config['mysql']['shell']['host']
        port = config['mysql']['shell']['port']
        dbhost = config['mysql']['server']['host']
        dbuser = config['mysql']['server']['user']
        dbpassword = config['mysql']['server']['password']

        env.user = user
        env.host = host
        env.port = port
        env.host_string = "%s@%s:%s" % (env.user, env.host, env.port)

        pretty_print('[+] Starting MySQL migrate', 'info')
        #	env.use_ssh_config = True

        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        #		pretty_print("Current working directory: %s" % os.getcwd())
        f = []
        for (dirpath, dirname, filenames) in os.walk(local_dir):
            f.extend(filenames)
            break
        f.sort()

        pretty_print('Files: %s' % f)
        os.chdir(local_dir)
        remote_dir = os.path.join(remote_dir, date)
        pretty_print('Creating directory %s' % remote_dir, 'info')
        run('mkdir -p %s' % remote_dir)
        for sql_file in f:
            pretty_print('Uploading file: %s' % sql_file, 'info')
            put(sql_file, remote_dir)

        with cd(remote_dir):
            for sql_file in f:
                pretty_print('Migrating file %s' % sql_file, 'info')
                with hide('running'):
                    run('mysql -u%s -p%s -h%s %s < %s' % (dbuser, dbpassword, dbhost, database, sql_file))
                #			run('rm %s' % file)

        pretty_print('[+] MySQL migrate finished.', 'info')


class DBMigrate(Plugin):
    command = 'db_migrate'
    config = None
    description = 'Arguments: <migration_folder> - migrate database to new version'

    def validate_config(self):
        return True

    def run(self, *args, **kwargs):
        self.validate_config()

        try:
            migration_dir = args[0]
        except IndexError:
            raise NotConfiguredError("Please provide local migration dir")

        pretty_print("[+] Starting database migration.", 'info')

        if not config:
            raise NotConfiguredError

        MySQLDBClone(config).run()
        if migration_dir:
            pretty_print("Migration directory provided. Running.", 'info')
            MySQLDBMigrate(config).run(migration_dir)
        else:
            pretty_print("No migration directory, omitting.", "info")

        MySQLDumpRemove(config).run()

        pretty_print("[+] Database migration finished.", 'info')