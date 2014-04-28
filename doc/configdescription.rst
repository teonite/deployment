
=========================
Configuration description
=========================

Sample configuration file
=========================
The config is in JSON format::

    {
        "source": {
            "git": {
                "repo": "git@git.teonite.net:teonite/status.git",
                "branch": "master",
                "local": "repo",
                "dirs" : ["src"]
            },
            "local": "test",
            "file": "arch.tar.gz"
        },
        "remote": {
            "host": "192.168.56.101",
            "user": "kkrzysztofik",
            "port": 22,
            "dir": "~",
            "clean": true
        },

        "deploy": {
            "dir": "Status",
            "pre": [
                "cat ~/.bashrc",
                "env"
            ],
            "post": [
                "pip install -r ~/Status/current/src/requirements.txt",
                "python ~/Status/current/src/tools/manage.py collectstatic --noinput"
            ]
        },

        "config": [
            "src/settings/gunicorn.conf.py",
            "src/settings/supervisor.conf",
            "src/settings/localsettings.py",
            "src/settings/logger.py"
        ],

        "mysql" : {
            "server" : {
                "host" : "localhost",
                "user" : "root",
                "password" : "pass",
                "port" : 3306,
                "database" : "status"
            },
            "shell" : {
                "dumpfile" : "temp.sql",
                "user" : "kkrzysztofik",
                "host" : "192.168.56.101",
                "port" : 22,
                "migration_dir" : "test"
            }
        },

        "supervisor" : {
            "host" : "192.168.56.101",
            "port" : 9001,
            "user" : "admin",
            "password" : "pass",
            "apps" : [
                "status",
                "status_celery"
            ]
        },

        "venv": {
            "requirements": ["requirements/production.txt"],
            "update": false,
            "dir": "env"
        },

        "logger" : {
            "version": 1,
            "formatters": {
                "simple": {
                    "format": "%(message)s"
                },
                "verbose": {
                    "format": "[%(asctime)s] \"%(message)s\"",
                    "datefmt": "%d/%b/%Y %H:%M:%S"
                }
            },

            "handlers": {
                "console": {
                    "level":"DEBUG",
                    "class":"logging.StreamHandler",
                    "formatter":"simple",
                    "stream" : "ext://sys.stdout"
                },
                "graypy": {
                    "level":"INFO",
                    "class":"graypy.GELFHandler",
                    "formatter":"verbose",
                    "host":"logs.teonite.net",
                    "port":12201
                }
            },

            "loggers": {
                "root": {
                    "handlers": ["console"],
                    "level": "INFO"
                },
                "deployment": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "qualname": "deployment",
                    "propagate": false
                }
            }
        }
    }


Configuration description
=========================
source
------
* *local* -
  Directory where all local files are placed (GIT repository, archive file)

  *Default:* current working directory
* *file* -
  Filename of file used to deploy on remote host, currently supported extensions are .tar.gz, .tgz, .tar

  *Default:* ``src.tar.gz``

git
^^^
Section connected with GIT repository

* *repo*
      Repository used to clone source.

      *Default:* fetched from current working directory

* *branch*
      Branch used to clone source

      *Default:* ``master``

* *local*
      Local repository directory, placed inside main local directory

      *Default:* current working directory

* *dirs*
      Directories and files which deployment archive is made of

      *Default:* whole repository

remote
------
During application deploy process, SSH with key-based authentication is used. You need to set host address and user. Ports default value is 22.

* *dir*
    Directory where archive is uploaded during deployment

    *Default:* current working directory

* *clean*
    Flag used to specify if archive after deployment has to be removed

deploy
------
* *dir*
    Directory where application lives

    *Default:* ``app``

* *pre*
    List of commands launched before deployment
* *post*
    List of commands launched after deployment

config
------
In this section you can configure list of files that should be copied after deployment. Using new format, paths are relative to ``deploy_dir\previous`` and are copied to ``deploy_dir\current``::

    new format:
        "config": [
            "path",
            "path2"
        ]

    old format: (deprecated):
        "config": {
            "display name": {
                "src": "absolute path to source file",
                "dst": "absolute path to destination"
            }
        }

venv
----
In this section, parameters of virtual environment are set.

* *dir*
    Directory where virtualenv should be located. If not defined, no check is made.

* *requirements*
    List of requirements files, that are installed after create/check of virtual env

    *Default:* ``["requirements/production.txt"]``

  *update*
    Update packages during check of virtual environment and requirements

    *Default:* ``false``

mysql
-----

shell
^^^^^
Shell from which all MySQL commands are executed, standard requrements are:

* *user*
* *host*
* *port*

Extra:

* *dumpfile*
    File used to make dumps of database and as a temporary file

* *migration_dir*
    Into this dir will be uploaded ``.sql`` files used in migration process

server
^^^^^^
MySQL server configuration used in all commands. Server must be accessible from shell, mentioned before

Requirements:

* *host*
* *user*
* *password*
* *port*
* *database*


supervisor
----------
Supervisor is a client/server system that allows its users to monitor and control a number of processes on UNIX-like operating systems.

Requirements:

* *host*
* *port*
* *user*
* *password*


* *apps*
    Supervisor processes which will be restarted

logger
------

The logger is configured by using ``logging.config.dictConfig()`` function, format is described here_

*Default*: same as listed above

.. _here: http://docs.python.org/2/library/logging.config.html#logging-config-dictschema