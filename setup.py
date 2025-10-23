from os.path import exists
from setuptools import setup

setup(name='kanren',
      version='0.3.0',
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
      long_description_content_type="text/markdown",
      zip_safe=False,
      classifiers=["Development Status :: 5 - Production/Stable",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: Implementation :: CPython",
                   "Programming Language :: Python :: Implementation :: PyPy",
      ],
)
