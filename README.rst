
.. |build_badge| image:: https://travis-ci.org/ABI-Software/MeshParser.svg?branch=master
    :target: https://travis-ci.org/ABI-Software/MeshParser

=========================
Mesh Parser |build_badge|
=========================

A Python library for parsing different mesh formats in to a list of points and a list of elements.  The element's nodes are identified by indexes into the point list array. 

Currently this library supports reading of the following formats:

- stl
- vrml
- vtk

Install
=======

::

  pip install git+https://github.com/ABI-Software/MeshParser.git

Usage
=====

::

  from meshparser.parser import MeshParser

  # It has some tests to determine the file format, if this fails you can set the format to use manually using a second argument 'use_parser'.  The 'use_parser' parameter must have one of the values from {'vtk', 'stl', 'vrml'}.
  p = MeshParser('file/to/load')
  # getPoints has an option to get the pared down points, i.e. all repeated points will be removed.
  n = p.getPoints()
  # getElements has two options, zero_based: returns point indexes that are zero based [false], pared: remove repeated points [false]
  e = p.getElements()
