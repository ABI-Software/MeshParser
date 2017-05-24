
===========
Mesh Parser
===========

A Python library for parsing different mesh formats in to a list of points and a list of elements.  The element's nodes are identified by indexes into the point list array. 

Usage
=====

:: 
  from meshparser import parser

  # It has smoe tests to determine the file format, if this files you can set the format to use manually using a second argument.
  p = parser('file/to/load')
  # getPoints has an option to get the pared down points, i.e. all repeated points will be removed.
  n = p.getPoints()
  # getElements has two options, zero_based: returns point indexes that are zero based [false], pared: remove repeated points [false]
 e = p.getElements()
