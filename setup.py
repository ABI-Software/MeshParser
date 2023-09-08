import os
from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'src', 'meshparser', 'version.txt')) as f:
    line = f.readline()
    version = line.strip()

dependencies = ["pointpare"]

long_description = """A Python library that parses different mesh format files into a Python dict 
ready for consumption by other libraries.
"""

setup(name=u'meshparser',
      version=version,
      description='A Small Python library for parsing files that describe a mesh.',
      long_description=long_description,
      classifiers=[],
      author=u'Hugh Sorby',
      author_email='h.sorby@auckland.ac.nz',
      url='https://github.com/ABI-Software/MeshParser',
      license='Apache',
      packages=find_packages('src', exclude=['tests', 'tests.*', ]),
      package_dir={'': 'src'},
      package_data={'': ['version.txt']},
      zip_safe=True,
      install_requires=dependencies,
      )
