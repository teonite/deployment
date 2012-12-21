[loggers]
keys=root,deployment

[handlers]
keys=console,graypy

[formatters]
keys=simple,verbose

[logger_root]
level=ERROR
handlers=console,graypy

[logger_deployment]
level=INFO
handlers=console,graypy
qualname=deployment

[handler_console]
class=StreamHandler
level=DEBUG
formatter=verbose
args=(sys.stdout,)

[handler_graypy]
class=graypy.GELFHandler
level=INFO
formatter=verbose
args=('logs.teonite.net', 12201)

[formatter_simple]
format=%(levelname)s %(message)s
datefmt=

[formatter_verbose]
format=[%(asctime)s] "%(message)s"
datefmt=%d/%b/%Y %H:%M:%S