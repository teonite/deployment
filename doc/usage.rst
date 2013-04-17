
=====
Usage
=====

Default directories for configuration file
==========================================
::

    ./src/conf/deploy.json
    ./src/conf/deployment.json
    ./src/settings/deploy.json
    ./src/settings/deployment.json
    ./conf/deploy.json
    ./conf/deployment.json
    ./settings/deploy.json
    ./settings/deployment.json
    ./src/conf/deployment/production.json
    ./src/settings/deployment/production.json
    ./conf/deployment/production.json
    ./settings/deployment/production.json

List of available commands
===========================

:deploy <local_subfolder>: deploys new version
:db_migrate <migration_folder>: migrate database to new version
:src_clone <folder> <subfolder>: clone repo to subfolder in local folder
:src_prepare <folder> <subfolder>: archive repo from subfolder in local folder to file
:src_upload: upload packed file from local folder to remote host
:src_remote_test: test remote host
:src_remote_extract <subfolder>: extract uploaded file to selected subfolder of deploy_dir, default current date
:src_remote_config: copy config from previous to current
:src_remote_deploy <subfolder>: deploys new version
:src_remote_rollback: backs to previous version
:src_pre_deploy: runs pre_deploy command from config file
:src_post_deploy: runs post_deploy command from config file
:mysql_db_clone <db_name> - clone db: <db_name> -> <db_name>_<current_date>_<current_time>
:mysql_db_migrate <migration_folder>: runs .sql files from selected folder
:mysql_db_dump: dump database to selected file
:mysql_db_restore: restore database from file
:mysql_dump_remove: remove dump file from remote host
:restart_supervisor <process_name> <process_name> ...: restart process in Supervisor

Requirements
============

Deployment requires the following modules:

* Python 2.7+ (3+ untested)
* Fabric 1.5.1+ (http://fabfile.org/)
* GitPython 0.3.2.RC1+ (http://pythonhosted.org/GitPython/0.3.2/index.html)
* graypy 0.2.7+ (https://github.com/severb/graypy)
