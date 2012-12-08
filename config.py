TYPE_DJANGO = 0
TYPE_OTHER = 1

TYPE = TYPE_OTHER # Type of project, if TYPE_DJANGO used - virtualenv is used, also requirements.txt is parsed

#### GIT CONFIG ####
GIT_REPO = ''
BRANCH = ''
LOCAL_DIR = ''

#### REMOTE CONFIG ####
FILE_NAME = ''
REMOTE_DIR = ''
REMOTE_HOST = ''
REMOTE_USER = ''

DEPLOY_DIR = ''

#### DJANGO-SPECIFIC ####
ENV_DIR = '' #


#### MYSQL CONFIG ####
MYSQL_HOST = '' # Set to empty string for localhost. Not used with sqlite3.
MYSQL_USER = ''
MYSQL_PASSWORD = ''
MYSQL_DATABASE = ''