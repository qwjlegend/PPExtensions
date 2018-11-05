import io
import os
import re

from distutils.core import setup

DESCRIPTION = "PayPal github extension for notebooks."
NAME = "extension logger"
PACKAGES = ['']
AUTHOR = "PayPal Notebooks Development Team"
LICENSE = 'PayPal Inc Internal Use only'


def read(path, encoding='utf-8'):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


def version(path):
    """Obtain the package version from a python file e.g. pkg/__init__.py
    See <https://packaging.python.org/en/latest/single_source_version.html>.
    """
    version_file = read(path)
    version_match = re.search(r"""^__version__ = ['"]([^'"]*)['"]""",
                              version_file, re.M)
    print(version_match)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = version('__init__.py')

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      license=LICENSE,
      packages=PACKAGES,
      classifiers=[
          'Development Status :: 1 - Beta',
          'License :: PayPal Inc Internal Use only',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.6'],
      extras_require={
          'dev': [
              'flake8'
          ]
      })
