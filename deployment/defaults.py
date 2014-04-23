__author__ = 'kkrzysztofik'

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
        "post": []
    },

    "venv": {
        "dir": "env",
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