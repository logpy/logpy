from os.path import exists
from setuptools import setup

setup(name='kanren',
      version='0.2.3',
      description='Logic Programming in python',
      url='http://github.com/logpy/logpy',
      author='Matthew Rocklin',
      author_email='mrocklin@gmail.com',
      license='BSD',
      packages=['kanren'],
      install_requires=open('requirements.txt').read().split('\n'),
      tests_require=[
          'pytest',
          'sympy'
      ],
      long_description=open('README.md').read() if exists("README.md") else "",
      zip_safe=False,
      classifiers=["Development Status :: 5 - Production/Stable",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6",
                   "Programming Language :: Python :: 3.7",
                   "Programming Language :: Python :: Implementation :: CPython",
                   "Programming Language :: Python :: Implementation :: PyPy",
      ],
)
