from distutils.core import setup

setup(
	name='deployment',
	version='1.0.0',
	author='TEONITE',
	author_email='robert@teonite.com',
	packages=['deployment'],
	scripts=['bin/deploy'],
	url='http://teonite.com/',
	description='Deployment and database migration tool.',
	long_description=open('README.txt').read(),
	install_requires=[
		"Fabric >= 1.5.1",
		"GitPython >= 0.3.2.RC1",
		"graypy >= 0.2.7",
		],
	data_files=[('teonite/deployment', ['conf/config.ini.template', 'conf/logger.conf.tpl']),],
)