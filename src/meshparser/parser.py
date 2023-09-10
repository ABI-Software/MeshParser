from meshparser.stlparser.parser import STLParser
from meshparser.vrmlparser.parser import VRMLParser
from meshparser.vtkparser.parser import VTKParser


class MeshParser(object):

    def __init__(self):
        self._parser = None

    def parse(self, filename, use_parser=None):
        if use_parser is None:
            # Try and determine which parser to use.
            vtk_parser = VTKParser()
            stl_parser = STLParser()
            vrml_parser = VRMLParser()
            if filename.endswith('.vtk'):
                if vtk_parser.can_parse(filename):
                    self._parser = vtk_parser
                else:
                    raise TypeError('Could not parse mesh as vtk mesh: {0}'.format(filename))
            elif filename.endswith('.stl'):
                if stl_parser.can_parse(filename):
                    self._parser = stl_parser
                else:
                    raise TypeError('Could not parse mesh as stl mesh: {0}'.format(filename))
            elif filename.endswith('.wrl'):
                if vrml_parser.can_parse(filename):
                    self._parser = vrml_parser
                else:
                    raise TypeError('Could not parse mesh as vrml mesh: {0}'.format(filename))
            else:
                if vtk_parser.can_parse(filename):
                    self._parser = vtk_parser
                elif stl_parser.can_parse(filename):
                    self._parser = stl_parser
                elif vrml_parser.can_parse(filename):
                    self._parser = vrml_parser
                else:
                    raise TypeError('Could not determine type of mesh to parse for filename: {0}'.format(filename))
        else:
            lower = use_parser.lowercase()
            if lower == 'vrml':
                self._parser = VRMLParser()
            elif lower == 'stk':
                self._parser = STLParser()
            elif lower == 'vtk':
                self._parser = VTKParser()
            else:
                raise NotImplementedError('A parser for the value: "{0}" has not been implemented.'.format(use_parser))

        self._parser.parse(filename)

    def get_points(self, pared=False):
        return self._parser.get_points(pared=pared)

    def get_elements(self, zero_based=True, pared=False):
        return self._parser.get_elements(zero_based=zero_based, pared=pared)
