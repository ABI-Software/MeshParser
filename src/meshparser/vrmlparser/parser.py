from meshparser.base.parser import BaseParser
from meshparser.exceptions import ParseError

    
class VRMLParser(BaseParser):

    def __init__(self):
        super(VRMLParser, self).__init__()
        self._data = {}

    def can_parse(self, filename):
        with open(filename) as f:
            lines = f.readlines()
            header_line = lines.pop(0)
            parseable = _check_header(header_line)

        return parseable

    def parse(self, filename):
        self._clear()
        scene = _VRMLScene()
        with open(filename) as f:
            lines = f.readlines()
            header_line = lines.pop(0)
            if not _check_header(header_line):
                raise ParseError('Header check failed')

            while lines:
                current_line = lines.pop(0)
                current_line = _remove_comment(current_line)
                line_elements = current_line.strip().split()
                while len(line_elements):
                    scene.parse(line_elements)

        self._data = scene.get_root()

        self._points = self._extract_points()
        self._elements = self._extract_elements()

    def _get_indexed_face_set(self):
        indexed_face_set = None
        if 'Transform' in self._data and 'children' in self._data['Transform']:
            if isinstance(self._data['Transform']['children'], list):
                shapes = self._data['Transform']['children']
                if len(shapes) > 1:
                    ParseError('Allow for more than two shapes in a single Transform.')

                shape = shapes[0]
                if 'Shape' in shape and 'geometry' in shape['Shape'] and 'IndexedFaceSet' in shape['Shape']['geometry']:
                    indexed_face_set = shape['Shape']['geometry']['IndexedFaceSet']

        return indexed_face_set

    def _extract_points(self):
        points = []
        indexed_face_set = self._get_indexed_face_set()
        if indexed_face_set is not None and 'coord' in indexed_face_set and 'Coordinate' in indexed_face_set['coord']:
            coordinates = indexed_face_set['coord']['Coordinate']
            if 'point' in coordinates:
                points = coordinates['point']

        return points

    def _extract_elements(self):
        elements = []
        indexed_face_set = self._get_indexed_face_set()
        if indexed_face_set is not None and 'coordIndex' in indexed_face_set:
            coordinate_indexes = indexed_face_set['coordIndex']
            elements = _convert_to_element_list(coordinate_indexes)

        return elements

        # if 'Transform' in self._data and self._data['Transform'] and len(self._data['Transform']) and \
        #         'Shape' in self._data['Transform'][0] and \
        #         'IndexedFaceSet' in self._data['Transform'][0]['Shape']:
        #     self._points = self._data['Transform'][0]['Shape']['IndexedFaceSet']['Coordinate']['point']
        #     element_list = self._data['Transform'][0]['Shape']['IndexedFaceSet']['coordIndex']
        #     self._elements = _convertToElementList(element_list)


def _remove_comment(line):
    """
    Removes any comments from a line.  A comment starts from a # symbol
    to the end of the line.  But don't remove from # symbol that are embedded
    in strings.
    """
    # First find just quotes and their indexes.
    quote_indexes = []
    hash_indexes = []
    for i, ch in enumerate(line):
        if ch == '"':
            quote_indexes.append(i)
            if i > 0 and line[i - 1] == "\\":
                quote_indexes.pop()
        elif ch == '#':
            hash_indexes.append(i)

    comment_marker_index = -1
    for hash_index in hash_indexes:
        quote_index_ranges = [quote_indexes[i:i + 2] for i in range(0, len(quote_indexes), 2)]
        if not _check_index_within_index_pairs(hash_index, quote_index_ranges):
            comment_marker_index = hash_index
            break

    if comment_marker_index >= 0:
        line = line[:comment_marker_index]
    return line


def _check_index_within_index_pairs(index, index_ranges):
    """
    Check that the index 'index' lies within the set of indexes.
    :param index: Index to determine whether it falls within the range or index pairs.
    :param index_ranges: A list of index pairs, monotonically increasing pairs.
    :return: True if the given index lies within a range specified by an index pair, False otherwise.
    """
    in_range = False
    for index_range in index_ranges:
        if index_range[0] < index < index_range[1]:
            in_range = True
    return in_range


class _VRMLScene(object):
    """
    Scene information object.
    """
    def __init__(self):
        self._root = {}
        self._state = None
        self._key = None

    def get_root(self):
        return self._root

    def parse(self, line_elements):
        # If no state is set then we are looking for a node.
        if self._state is None:
            element = line_elements.pop(0)
            if _is_node(element):
                self._state = _get_vrml_node(element)
                self._key = element
                self._root[element] = {}
            else:
                raise ParseError('Unknown node: "{0}" where node expected.'.format(element))
        else:
            self._state.parse(line_elements)
            if self._state.is_finished():
                self._root[self._key] = self._state.get_data()
                self._state = None


class _BaseParse:
    """
    Base object for all parseable classes.
    """
    def __init__(self):
        self._finished = False
        self._data = None

    def is_finished(self):
        return self._finished

    def set_finished(self, state=True):
        self._finished = state

    def get_data(self):
        return self._data


class _BaseMultiAble(_BaseParse):
    """
    Base class for classes that are able to parse multiple or single items.
    """
    def __init__(self):
        super(_BaseMultiAble, self).__init__()
        self._multi = False
        self._open_marker = '['
        self._close_marker = ']'

    def set_multi(self, state=True):
        self._multi = state

    def is_multi(self):
        return self._multi

    def is_open_marker(self, marker):
        return marker == self._open_marker

    def is_close_marker(self, marker):
        return marker == self._close_marker

    def add_data(self, data):
        if self._multi:
            self._data.append(data)
        else:
            self._data = data


class _FNode(_BaseMultiAble):
    """
    Parses a node, or a multi node array.
    """
    def __init__(self):
        super(_FNode, self).__init__()
        self._active_key = None
        self._active_state = None

    def clear(self):
        self._active_key = None
        self._active_state = None

    def parse(self, line_elements):
        while line_elements and not self.is_finished():
            element = line_elements[0]
            consume = True
            if self.is_open_marker(element):
                self._data = []
                self._multi = True
            elif self._active_state is not None:
                consume = False
                self._active_state.parse(line_elements)
                if self._active_state.is_finished():
                    self.add_data({self._active_key: self._active_state.get_data()})
                    self.clear()
                    if not self._multi:
                        self._finished = True
            elif self.is_close_marker(element):
                self._finished = True
            elif self._active_state is None:
                if _is_node(element):
                    self._active_key = element
                    self._active_state = _get_vrml_node(element)
                elif element == 'NULL':
                    self._data = None
                    self._finished = True
                else:
                    raise ParseError('Unknown node: "{0}" where node expected.'.format(element))

            if consume:
                line_elements.pop(0)


class _BaseFloat(_BaseMultiAble):
    """
    Parses a set number of floats.
    """
    def __init__(self, float_count=3):
        super(_BaseFloat, self).__init__()
        self._float_count = float_count
        self._current = []

    def parse(self, line_elements):
        while line_elements and not self.is_finished():
            element = line_elements.pop(0)
            if self._data is None:
                self._data = []

            if self.is_open_marker(element):
                self._multi = True
            elif self.is_close_marker(element):
                self._finished = True
            else:
                if element[-1] == ',':
                    element = element[:-1]
                self._current.append(float(element))
                if len(self._current) == self._float_count:
                    self.add_data(self._current)
                    self._current = []
                    if not self._multi:
                        self.set_finished()


class _BaseInt(_BaseMultiAble):
    """
    Parses a set number of floats.
    """
    def __init__(self):
        super(_BaseInt, self).__init__()

    def parse(self, line_elements):
        while line_elements and not self.is_finished():
            element = line_elements.pop(0)
            if self._data is None:
                self._data = []

            if self.is_open_marker(element):
                self._multi = True
            elif self.is_close_marker(element):
                self._finished = True
            else:
                if element[-1] == ',':
                    element = element[:-1]

                self.add_data(int(element))
                if not self._multi:
                    self.set_finished()


class _FInt32(_BaseInt):
    """
    Parses single or a list of integers.
    """

class _FVec3f(_BaseFloat):
    """
    Parses three floats or a multi floats.
    """
    def __init__(self):
        super(_FVec3f, self).__init__(3)


class _FColour(_BaseFloat):
    """
    Float based colour.
    """
    def __init__(self):
        super(_FColour, self).__init__(3)


class _FFloat(_BaseFloat):
    """
    Float based colour.
    """
    def __init__(self):
        super(_FFloat, self).__init__(1)


class _FRotation(_BaseFloat):
    """
    Parses four floats or a multi four floats.
    """
    def __init__(self):
        super(_FRotation, self).__init__(4)


class _FString(_BaseMultiAble):
    """
    Parses a single string or multi string field or event.
    """
    def __init__(self):
        super(_FString, self).__init__()
        self._parsing_string = False

    def parse(self, line_elements):
        while line_elements and not self.is_finished():
            element = line_elements.pop(0)
            if self.is_open_marker(element):
                #  Multi string
                self.set_multi()
                self._data = []
            elif self.is_close_marker(element):
                self.set_multi(False)
                self.set_finished()
            else:
                if self._data is None:
                    self._data = ''
                index = element.find("\"")
                # Find the index again if the quote is escaped.
                while index > 0 and element[index - 1] == '\\':
                    index = element.find("\"", index + 1)
                if self._parsing_string:
                    inclusive_index = index + 1
                    if self.is_multi():
                        stem_string = self._data.pop()
                        if index > -1:
                            stem_string += ' ' + element[:inclusive_index]
                        else:
                            stem_string += ' ' + element
                        self._data.append(stem_string)
                    else:
                        if index > -1:
                            self._data += ' ' + element[:inclusive_index]
                        else:
                            self._data += ' ' + element
                    if index > -1:
                        self._parsing_string = False
                        if not self.is_multi():
                            self.set_finished()
                else:
                    self._parsing_string = True
                    if self.is_multi():
                        self._data.append(element)
                    else:
                        self._data += element


class _BaseNode(_BaseParse):
    """
    Base node for all nodes.
    """
    def __init__(self):
        super(_BaseNode, self).__init__()
        self._name = ''
        self._active_field = None
        self._field_parser = None
        self._fields = []
        self._field_types = []
        self._open_marker = '{'
        self._close_marker = '}'

    def clear(self):
        self._active_field = None
        self._field_parser = None

    def get_name(self):
        return self._name

    def is_open_marker(self, marker):
        return marker == self._open_marker

    def is_close_marker(self, marker):
        return marker == self._close_marker

    def get_parser(self, field_name):
        index = self._fields.index(field_name)
        field_type = self._field_types[index]
        if field_type in ['SFString', 'MFString']:
            parser = _FString()
        elif field_type in ['SFVec3f', 'MFVec3f']:
            parser = _FVec3f()
        elif field_type in ['SFRotation']:
            parser = _FRotation()
        elif field_type in ['SFFloat']:
            parser = _FFloat()
        elif field_type in ['SFColour']:
            parser = _FColour()
        elif field_type in ['SFNode', 'MFNode']:
            parser = _FNode()
        elif field_type in ['MFInt32']:
            parser = _FInt32()
        else:
            raise ParseError('Unknown field type: "{0}".'.format(field_type))

        return parser

    def add_data(self, key, data):
        self._data[key] = data

    def parse(self, line_elements):
        while line_elements and not self.is_finished():
            element = line_elements[0]
            consume = True
            if self.is_open_marker(element):
                self._data = {}
            elif self._active_field is not None:
                consume = False
                self._field_parser.parse(line_elements)
                if self._field_parser.is_finished():
                    self.add_data(self._active_field, self._field_parser.get_data())
                    self.clear()
            elif self.is_close_marker(element):
                self.set_finished()
            else:
                self._active_field = element
                self._field_parser = self.get_parser(element)

            if consume:
                line_elements.pop(0)


class _WorldInfoNode(_BaseNode):
    """
    WorldInfo node.  Has optional fields: title (SFString), info (MFString).
    """
    def __init__(self):
        super(_WorldInfoNode, self).__init__()
        self._name = 'WorldInfo'
        self._fields = ['title', 'info']
        self._field_types = ['SFString', 'MFString']


class _ShapeNode(_BaseNode):
    """
    Shape node.  Has two optional fields.
    """
    def __init__(self):
        super(_ShapeNode, self).__init__()
        self._name = 'Shape'
        self._fields = ['appearance', 'geometry']
        self._field_types = ['MFNode', 'MFNode']


class _AppearanceNode(_BaseNode):
    """
    Shape node.  Has two optional fields.
    """
    def __init__(self):
        super(_AppearanceNode, self).__init__()
        self._name = 'Appearance'
        self._fields = ['material', 'texture', 'textureTransform']
        self._field_types = ['MFNode', 'MFNode', 'MFNode']


class _MaterialNode(_BaseNode):
    """
    Shape node.  Has two optional fields.
    """
    def __init__(self):
        super(_MaterialNode, self).__init__()
        self._name = 'Material'
        self._fields = ['ambientIntensity', 'diffuseColor', 'emissiveColor', 'shininess', 'specularColor', 'transparency']
        self._field_types = ['SFFloat', 'SFColour', 'SFColour', 'SFFloat', 'SFColour', 'SFFloat']


class _TransformNode(_BaseNode):
    """
    Transform node.  Has eight optional fields.
    """
    def __init__(self):
        super(_TransformNode, self).__init__()
        self._name = 'Transform'
        self._fields = ['center', 'children', 'rotation', 'scale',
                        'scaleOrientation', 'translation', 'bboxCenter', 'bboxSize']
        self._field_types = ['SFVec3f', 'MFNode', 'SFRotation', 'SFVec3f',
                             'SFRotation', 'SFVec3f', 'SFVec3f', 'SFVec3f']


class _IndexedFaceSetNode(_BaseNode):
    """
    Indexed face set node.  Has 14 optional fields.
    """
    def __init__(self):
        super(_IndexedFaceSetNode, self).__init__()
        self._name = 'IndexedFaceSet'
        self._fields = ['color', 'coord', 'normal', 'texCoord', 'ccw', 'colorIndex', 'colorPerVertex', 'convex', 'coordIndex', 'creaseAngle', 'normalIndex', 'normalPerVertex', 'solid', 'texCoordIndex']
        self._field_types = ['SFNode', 'SFNode', 'SFNode', 'SFNode', 'SFBool', 'MFInt32', 'SFBool', 'SFBool', 'MFInt32', 'SFFloat', 'MFInt32', 'SFBool', 'SFBool', 'MFInt32']


class _CoordinateNode(_BaseNode):
    """
    Coordinate node.  Has one optional field.
    """
    def __init__(self):
        super(_CoordinateNode, self).__init__()
        self._name = 'Coordinate'
        self._fields = ['point']
        self._field_types = ['MFVec3f']


class _NormalNode(_BaseNode):
    """
    Normal node.  Has one optional field.
    """
    def __init__(self):
        super(_NormalNode, self).__init__()
        self._name = 'Normal'
        self._fields = ['vector']
        self._field_types = ['MFVec3f']


def _check_header(header):
    vrml, version, encoding = header.strip().split(' ')
    # VRML V2.0 utf8
    if vrml == '#VRML' and version == 'V2.0' and encoding == 'utf8':
        return True
    
    return False


def _convert_to_element_list(elements_list):
    """
    Take a list of element node indexes deliminated by -1 and convert
    it into a list element node indexes list.
    """
    elements = []
    current_element = []
    for node_index in elements_list:
        if node_index == -1:
            elements.append(current_element)
            current_element = []
        else:
            current_element.append(node_index)

    return elements


def _get_known_nodes():
    """
    Return a list of known node names.  Taken from the subclasses of _BaseNode.
    :return: List of known node names.
    """
    return [n().get_name() for n in _BaseNode.__subclasses__()]


def _is_node(name):
    """
    Determine if the given name is a valid node name.
    :param name: Name of the node to test.
    :return: True if the node is known, False otherwise.
    """
    known_nodes = _get_known_nodes()
    if name in known_nodes:
        return True

    return False


def _get_vrml_node(name):
    """
    Return the node object that matches the given named node.  The name must be a valid VRML node name.
    :param name: The name of the object to return.
    :return: The VRML Node object that matches the given name.
    """
    known_nodes = _get_known_nodes()
    index = known_nodes.index(name)
    return _BaseNode.__subclasses__()[index]()
