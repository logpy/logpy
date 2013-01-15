from os.path import exists
from setuptools import setup

setup(name='logic',
      version='0.1.2',
      description='Logic Programming in python',
      url='http://github.com/logpy/logpy',
      author='Matthew Rocklin',
      author_email='mrocklin@gmail.com',
      license='BSD',
      packages=['logpy'],
      long_description=open('README.md').read() if exists("README.md") else "",
      zip_safe=False)
