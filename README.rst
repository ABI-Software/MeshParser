
.. |build_badge| image:: https://travis-ci.org/ABI-Software/MeshParser.svg?branch=main
    :target: https://travis-ci.org/ABI-Software/MeshParser

=========================
Mesh Parser |build_badge|
=========================

A Python library for parsing different mesh formats in to a list of points and a list of elements.  The element's 
nodes are identified by indexes into the point list array.

This project uses `semantic versioning <http://semver.org/>`_ when versioning the software.

Currently this library supports reading of the following formats:

- stl
- vrml
- vtk

Install
=======

::

  pip install MeshParser

Usage
=====

::

  from meshparser.parser import MeshParser

  # It has some tests to determine the file format, if this fails you can set the format to use manually 
  # using a second argument 'use_parser'.  The 'use_parser' parameter must have one of the values from {'vtk', 'stl', 'vrml'}.
  p = MeshParser()
  p.parse('file/to/parse')
  # get_points has an option to get the pared down points, i.e. all repeated points will be removed.
  n = p.get_points()
  # get_elements has two options, zero_based: returns point indexes that are zero based [false], pared: remove repeated points [false]
  e = p.get_elements()

Advanced usage::

  from meshparser.parser import parse_mesh
  from meshparser.manipulation import calculate_centre_of_mass, translate, rotate
  from meshparser.printer import print_mesh

  mesh = parse_mesh('<absolute-path-to-in.stl>')
  com = calculate_centre_of_mass(mesh)
  mcom = [-val for val in com]
  mesh = translate(mesh, mcom)
  mesh = rotate(mesh, [1, 0, 0], 90)

  print_mesh(mesh, '<absolute-path-to-out.stl>')
