
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

        "config": {
            "gunicorn": {
                "src": "/home/kkrzysztofik/Status/previous/src/settings/gunicorn.conf.py",
                "dst": "/home/kkrzysztofik/Status/current/src/settings/gunicorn.conf.py"
            },
            "supervisor": {
                "src": "/home/kkrzysztofik/Status/previous/src/settings/supervisor.conf",
                "dst": "/home/kkrzysztofik/Status/current/src/settings/supervisor.conf"
            },
            "localsettings": {
                "src": "/home/kkrzysztofik/Status/previous/src/settings/localsettings.py",
                "dst": "/home/kkrzysztofik/Status/current/src/settings/localsettings.py"
            },
            "logger": {
                "src": "/home/kkrzysztofik/Status/previous/src/settings/logger.conf",
                "dst": "/home/kkrzysztofik/Status/current/src/settings/logger.conf"
            }
        },

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

        "logger" : {
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
                    "level":"DEBUG",
                    "class":"logging.StreamHandler",
                    "formatter":"verbose",
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
                    "level": "DEBUG"
                },
                "deployment": {
                    "handlers": ["console"],
                    "level": "DEBUG",
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
* git

    * repo
    * branch
    * local
    * dirs

* local
* file

remote
------
* host
* user
* port
* dir
* clean

deploy
------
 "dir": "Status",
            "pre": [
                "cat ~/.bashrc",
                "env"
            ],
            "post": [
                "pip install -r ~/Status/current/src/requirements.txt",
                "python ~/Status/current/src/tools/manage.py collectstatic --noinput"
            ]

config
------

            "gunicorn": {
                "src": "/home/kkrzysztofik/Status/previous/src/settings/gunicorn.conf.py",
                "dst": "/home/kkrzysztofik/Status/current/src/settings/gunicorn.conf.py"
            },
            "supervisor": {
                "src": "/home/kkrzysztofik/Status/previous/src/settings/supervisor.conf",
                "dst": "/home/kkrzysztofik/Status/current/src/settings/supervisor.conf"
            },
            "localsettings": {
                "src": "/home/kkrzysztofik/Status/previous/src/settings/localsettings.py",
                "dst": "/home/kkrzysztofik/Status/current/src/settings/localsettings.py"
            },
            "logger": {
                "src": "/home/kkrzysztofik/Status/previous/src/settings/logger.conf",
                "dst": "/home/kkrzysztofik/Status/current/src/settings/logger.conf"
            }

mysql
-----

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

supervisor
----------
            "host" : "192.168.56.101",
            "port" : 9001,
            "user" : "admin",
            "password" : "pass",
            "apps" : [
                "status",
                "status_celery"
            ]

logger
------
