import sys
import os
from setuptools import find_packages, setup

sys.path.insert(0, os.path.join(os.path.abspath(os.path.curdir), 'dot-relay'))

name = 'DoT-relay'

setup(name=name,
      version='0.1',
      description='Python DNS over TLS relay.',
      author='A.V.',
      packages=find_packages(),
      )
