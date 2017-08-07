"""
setup
"""

from setuptools import setup, find_packages
from pip.req import parse_requirements

version = '0.1.3'

def _load_requires_from_file(filepath):
    install_reqs = parse_requirements(filepath, session=False)
    return [str(ir.req) for ir in install_reqs]

def _install_requires():
    return _load_requires_from_file('requirements.txt')

def _test_requires():
    return _load_requires_from_file('requirements/dev.txt')

setup(name='chatty',
      version=version,
      description="chatty bot",
      long_description="""\
""",
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=_install_requires(),
      tests_require=_test_requires(),
      entry_points={},
      )
