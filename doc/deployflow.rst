
===============
Deployment flow
===============

Folder structure
================
::

    remote_dir
    |-deploy_dir
    |   |-20130411_212959
    |   |-20130411_213213
    |   |-20130412_181014
    |   |-current -> 20130412_181014
    |   |-previous -> 20130411_213213
    |-migration_dir
    |-upload_dir
    |-dump_file

Deployment process
==================
1. Test remote server
    Checks if connection to remote server is possible.

2. Execute pre-deploy commands
3. Get sources
    If local git repository is found, it will be pulled, else will be cloned.

4. Archive sources
5. Upload sources to remote server
6. Extract source to target subfolder
7. Switch current/previous links
8. Copy config files
9. Run post-deploy commands