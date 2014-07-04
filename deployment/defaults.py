#
# Deployment, provisioning and database migration tool
#
# Copyright (C) 2012-2014 TEONITE
# Copyright (C) 2012-2014 Krzysztof Krzysztofik <krzysztof.krzysztofik@teonite.com>
#

__author__ = 'Krzysztof Krzysztofik'

config = {
    "source": {
        "git": {
            "repo": "",
            "branch": "master",
            "local": ".",
            "dirs": []
        },
        "local": ".",
        "file": "src.tar.gz"
    },

    "remote": {
        "host": "",
        "user": "",
        "port": 22,
        "dir": "~",
        "clean": True
    },

    "deploy": {
        "dir": "app",
        "pre": [],
        "post": [],
        "changelog": "",
        "all_commits": True
    },

    "venv": {
        "dir": "",
        "requirements": ["requirements/production.txt"],
        "update": False
    },

    "config": {
    },

    "mysql": {
        "server": {
            "host": "localhost",
            "user": "root",
            "password": "",
            "port": 3306,
            "database": ""
        },
        "shell": {
            "dumpfile": "temp.sql",
            "user": "",
            "host": "",
            "port": 22,
            "migration_dir": ""
        }
    },

    "supervisor": {
        "host": "",
        "port": 9001,
        "user": "admin",
        "password": "",
        "apps": []
    },

    "mail": {
        "project_name": "",

        "from_mail": "",

        "server": {
            "user": "",
            "password": "",
            "host": "localhost",
            "port": "25",
        },

        "people": [
        ],

        "template_path": "",
    }
}

path_list = [
        './config.json',
        './deployment/production.json',
        './deployment/development.json',
        './src/conf/deploy.json',
        './src/conf/deployment.json',
        './src/settings/deploy.json',
        './src/settings/deployment.json',
        './conf/deploy.json',
        './conf/deployment.json',
        './settings/deploy.json',
        './settings/deployment.json',
        './src/conf/deployment/production.json',
        './src/settings/deployment/production.json',
        './conf/deployment/production.json',
        './settings/deployment/production.json'
]

LOGGING = {
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
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
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
            "propagate": False
        }
    }
}

SUBJECT_TEMPLATE = "[{project_name}] New version deployed."
MESSAGE_TEMPLATE = "New version of {project_name} has been deployed."