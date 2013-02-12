[Source]
GIT_REPO = gitolite@git.teonite.net:TEONITE/sample.git
GIT_BRANCH = master
GIT_REPO_LOCAL = test
LOCAL_DIR = test
FILE_NAME = src.tar

UPLOAD_DIR = ~
REMOTE_HOST = 192.168.56.101
REMOTE_USER = kmk
UPLOAD_CLEAN = False

DEPLOY_DIR = deploy
CONFIG_TO_COPY = [{"dest": "logger.conf", "src": "logger.conf.tpl"}]
POST_DEPLOY = echo "DONE"
PRE_DEPLOY = echo "START"

; not used in this version of script
ENV_DIR = ''

[Migrate_MySQL]
MYSQL_DUMPFILE = temp.sql
MYSQL_SHELL_USER = kmk
MYSQL_SHELL_HOST = 192.168.56.101
MYSQL_HOST = localhost
MYSQL_USER = root
MYSQL_PASSWORD = test
MYSQL_DATABASE = base
MYSQL_REMOTE_DIR = test