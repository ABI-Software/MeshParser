from setuptools import setup

dependencies = []

long_description = """A Python library that parses different mesh format files into a Python dict 
ready for consumption by other libraries.
"""

setup(name=u'meshparser',
      version='0.1.0',
      description='A Small Python library for parsing files.',
      long_description=long_description,
      classifiers=[],
      author=u'Hugh Sorby',
      author_email='',
      url='http://pypi.org/meshparser',
      license='GPL',
      packages=['meshparser'],
      package_dir={'': 'src'},
      zip_safe=True,
      install_requires=dependencies,
      )
