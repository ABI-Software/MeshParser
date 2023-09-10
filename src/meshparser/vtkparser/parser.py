from meshparser.base.parser import BaseParser


class VTKParser(BaseParser):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(VTKParser, self).__init__()

    def can_parse(self, filename):
        state = _HeaderState(self)
        with open(filename) as f:
            lines = f.readlines()
            header_line = lines.pop(0)
            try:
                parseable = state.parse(header_line.rstrip())
            except SyntaxError:
                parseable = False

        return parseable

    def parse(self, filename):
        self._clear()

        current_state = self._next_state(_InitState())
        with open(filename) as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip()
                if current_state is not None and current_state.parse(line):
                    current_state = self._next_state(current_state)

    def _next_state(self, current_state):
        state_map = {
            _InitState: _HeaderState(self),
            _HeaderState: _TitleState(self),
            _TitleState: _DataTypeState(self),
            _DataTypeState: _TopologyState(self),
            _TopologyState: _DatasetAttributesState(self),
            _DatasetAttributesState: None,
        }
        return state_map[type(current_state)]


class _BaseState(object):

    def __init__(self, parent=None):
        self._parent = parent

    def parse(self, line):
        """
        All instantiated classes must define this method.
        """


class _InitState(_BaseState):
    pass


class _HeaderState(_BaseState):

    def parse(self, line):
        matching = [s for s in KNOWN_FILE_FORMATS if line == s]
        if matching:
            return True

        raise SyntaxError('Unknown file format syntax.')


class _TitleState(_BaseState):

    def parse(self, line):
        return True


class _DataTypeState(_BaseState):

    def parse(self, line):
        if line == "ASCII":
            return True

        raise NotImplementedError('Handling of binary data has not been implemented.')


class _TopologyState(_BaseState):

    def __init__(self, parent):
        super(_TopologyState, self).__init__(parent)
        self._dataset_type = None
        self._processing = None

    def parse(self, line):
        status = False
        if self._dataset_type is None:
            # Determine dataset type
            parts = line.split(' ')
            if len(parts) > 1 and parts[0] == 'DATASET':
                self._dataset_type = parts[1]

        elif self._dataset_type == 'POLYDATA':
            if self._processing is None:
                # Determine data type
                parts = line.split(' ')
                if len(parts) > 2:
                    self._processing = {'type': parts[0],
                                        'n': int(parts[1]),
                                        'progress': 0,
                    }
                    if self._processing['type'] == 'POINTS':
                        self._processing['datatype'] = parts[2]
                        self._processing['current_pt'] = []
                    else:
                        self._processing['size'] = int(parts[2])
            elif self._processing['type'] == 'POINTS':
                parts = line.split(' ')
                for part in parts:
                    if self._processing['datatype'] == 'float':
                        self._processing['current_pt'].append(float(part))
                    if len(self._processing['current_pt']) == 3:
                        self._parent._points.append(self._processing['current_pt'])
                        self._processing['current_pt'] = []
                        self._processing['progress'] += 1

                if self._processing['progress'] == self._processing['n']:
                    self._processing = None

            elif self._processing['type'] == 'POLYGONS':
                parts = line.split(' ')
                if len(parts):
                    polygon_size = int(parts[0])
                    if polygon_size == len(parts[1:]):
                        self._parent._elements.append([int(index) for index in parts[1:]])
                    self._processing['progress'] += 1

                if self._processing['progress'] == self._processing['n']:
                    status = True

        return status


class _DatasetAttributesState(_BaseState):

    def parse(self, line):
        return True


KNOWN_FILE_FORMATS = [
    "# vtk DataFile Version 3.0",
]
