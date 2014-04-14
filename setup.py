from setuptools import setup
from deployment.version import version

readme = []
with open('README.rst', 'r') as fh:
    readme = fh.readlines()

setup(
    name='deployment',
    version=version,
    author='TEONITE',
    author_email='robert@teonite.com',
    packages=['deployment'],
    scripts=['deploy'],
    url='http://teonite.com/',
    description='Deployment and database migration tool.',
    long_description='\n'.join(readme),
    license='Proprietary',
    install_requires=[
        "Fabric >= 1.5.1",
        "GitPython >= 0.3.2.RC1",
        "graypy >= 0.2.7",
        ""
    ],
    data_files=[('deployment/conf/', ['conf/conf.json.template'])]
)
