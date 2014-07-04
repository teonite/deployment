
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

* **db_migrate:**
    * Migrate database to new version
    * *Arguments:* <migration_folder>

* **deploy:**
    * Deploys new version
    * *Arguments:* <local_subfolder>

* **mysql_db_clone:**
    * Clone db: <db_name> -> <db_name>_<current_date>_<current_time>
    * *Arguments:* <db_name>

* **mysql_db_dump:**
    * Dump database to selected file
    * *Arguments:* <database>

* **mysql_db_migrate:**
    * Runs .sql files from selected folder
    * *Arguments:* <migration_folder>

* **mysql_db_restore:**
    * Restore database from file
    * *Arguments:* <database>

* **mysql_dump_remove:**
    * Remove dump file from remote host
    * *Arguments:* None

* **restart_supervisor:**
    * Restart process in Supervisor
    * *Arguments:* <process_name> <process_name> ...

* **src_clean:**
    - Delete file/folder provided as argument
    - *Arguments:* <to_delete>

* **src_clone:**
    - Clone repo to subfolder in local folder
    - *Arguments:* <folder> <subfolder>

* **src_post_deploy:**
    - Runs post_deploy command from config file
    - *Arguments:* None

* **src_pre_deploy:**
    - Runs pre_deploy command from config file
    - *Arguments:* None

* **src_prepare:**
    - Archive repo from subfolder in local folder to file
    - *Arguments:* <folder> <subfolder>

* **src_remote_config:**
    - copy config from previous to current
    - *Arguments:* None

* **src_remote_deploy:**
    - deploys new version
    - *Arguments:* <subfolder>

* **src_remote_extract:**
    - extract uploaded file to selected subfolder of deploy_dir, default current date
    - *Arguments:* <subfolder>

* **src_remote_rollback:**
    - backs to previous version
    - *Arguments:* None

* **src_remote_test:**
    - test remote host
    - *Arguments:* <user> <host>

* **src_remote_venv:**
    - check if venv exists, if not it will be created, and populated with requirements.txt
    - *Arguments:* <directory>

* **src_upload:**
    - upload packed file from local folder to remote host
    - *Arguments:* none

Requirements
============

Deployment requires the following modules:

* Python 2.7+ (3+ untested)
* Fabric 1.5.1+ (http://fabfile.org/)
* GitPython 0.3.2.RC1+ (http://pythonhosted.org/GitPython/0.3.2/index.html)