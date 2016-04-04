import os
from setuptools import setup, find_packages

here = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(here, 'requirements.txt')) as f:
    REQUIREMENTS = [line for line in iter(f) if not line.startswith('--')]


setup(name='bvs-worker',
      version="0.0.1",
      packages=find_packages(exclude=['*.tests']),
      install_requires=REQUIREMENTS,
      include_package_data=True,
      zip_safe=False,
      )
