__author__ = 'kkrzysztofik'

config = {
    "source": {
        "git": {
            "repo": ".",
            "branch": "master",
            "local": "repo",
            "dirs": []
        },
        "local": "test",
        "file": "arch.tar.gz"
    },

    "remote": {
        "host": "192.168.56.101",
        "user": "kkrzysztofik",
        "port": 22,
        "dir": "~",
        "clean": True
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

    "mysql": {
        "server": {
            "host": "localhost",
            "user": "root",
            "password": "pass",
            "port": 3306,
            "database": "status"
        },
        "shell": {
            "dumpfile": "temp.sql",
            "user": "kkrzysztofik",
            "host": "192.168.56.101",
            "port": 22,
            "migration_dir": "test"
        }
    },

    "supervisor": {
        "host": "",
        "port": 9001,
        "user": "admin",
        "password": "",
        "apps": []
    }
}

path_list = [
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