'''
Created on Jun 18, 2015

@author: hsorby
'''

keywords = ['Transform']

class MODES(object):
    
    KEYWORD = 1
    LABEL = 2
    
    
class SIGNALS(object):
    
    COMPLETE = 1
    CHILD = 2
    
    
class VRMLParser(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._points = []
        self._elements = []
        self._data = {}
        self._state = _RootState()
           
    def parse(self, filename):
        state = _RootState()
        with open(filename) as f:
            lines = f.readlines()
            header_line = lines.pop(0)
            if not _checkHeader(header_line):
                print('Error: Header check failed')
                return
            
            parsings = 0
            while lines and state is not None:
                current_line = lines.pop(0)
                line_elements = current_line.strip().split(' ')
                while len(line_elements):
#                     print(parsings, line_elements)
                    parsings += 1
                    line_elements = state.parse(line_elements)
                    state = state.activeState()
                    
        self._data = state.getData()
        if 'Transform' in self._data and self._data['Transform'] and len(self._data['Transform']) and 'Shape' in self._data['Transform'][0] and 'IndexedFaceSet' in self._data['Transform'][0]['Shape']:
            self._points = self._data['Transform'][0]['Shape']['IndexedFaceSet']['Coordinate']['point']
            self._elements = self._data['Transform'][0]['Shape']['IndexedFaceSet']['coordIndex']

    def getPoints(self):
        return self._points
    
    def getElements(self):
        return self._elements
    
class _BaseState(object):
    
    def __init__(self, parent=None):
        self._parent = parent
        self._complete = False
        self._active_state = self
        self._data = None
        self._key = None
        self._label = None
        self._mode = None
        
    def isComplete(self):
        return self._complete
    
    def isActive(self):
        return self._active_state is not None

    def parse(self, line_elements):
        raise NotImplementedError()
    
    def activeState(self):
        return self._active_state
    
    def getKey(self):
        return self._key
    
    def getData(self):
        return self._data
    
    def setData(self, data):
        if isinstance(self._data, dict):
            self._data[self._key] = data
        else:
            self._data.append(data)


class _RootState(_BaseState):
    
    def parse(self, line_elements):
        if line_elements:
            element = line_elements.pop(0)
            if element == 'Transform':
                self._key = 'Transform'
            elif _isOpenScopeMarker(element):
                self._data = _getTypeForMarker(element)
                self._active_state = _TransformState(self)
            elif _isCloseScopeMarker(element):
                data = self._active_state.getData()
                self._data[self._key] = data
                self._active_state = None
                
        return line_elements
    
    def getData(self):
        if self._active_state != self:
            data = self._active_state.getData()
            self._data[self._key] = data
            return self._data
    

class _TransformState(_BaseState):
    
    def parse(self, line_elements):
        if line_elements:
            element = line_elements.pop(0)
            if element == 'children':
                self._key = 'children'
            elif _isOpenScopeMarker(element):
                self._data = _getTypeForMarker(element)
                self._active_state = _ChildState(self)
            elif _isCloseScopeMarker(element):
                self._data.append(self._active_state.getData())
                self._active_state = self._parent
        
        return line_elements


class _ChildState(_BaseState):
    
    def parse(self, line_elements):
        if line_elements:
            element = line_elements.pop(0)
            if element in ['Shape']:
                self._key = element
                self._mode = element
            elif _isOpenScopeMarker(element):
                self._data = _getTypeForMarker(element)
                self._active_state = _ShapeState(self)
            elif _isCloseScopeMarker(element):
                if self._key is not None:
                    self._data[self._key] = self._active_state.getData()
                self._active_state = self._parent
            
        return line_elements


class _ShapeState(_BaseState):
    
    def parse(self, line_elements):
        if line_elements:
            if self._data is None:
                self._data = {}
                
            element = line_elements.pop(0)
            if element in ['IndexedFaceSet', 'Appearance']:
                self._active_state = self
                self._key = element
                if self._previous_element:
                    self._label = self._previous_element
            elif _isOpenScopeMarker(element):
                self._data[self._key] = _getTypeForMarker(element)
                if self._label is not None:
                    self._data[self._key]['label'] = self._label
                self._active_state = _getStateForNode(self._key, self)
            elif _isCloseScopeMarker(element):
                self._parent.setData(self._data)
                self._active_state = self._parent
            elif element:
                self._active_state = self
                self._previous_element = element
                
        return line_elements


class _AppearanceState(_BaseState):
    
    def parse(self, line_elements):
        if line_elements:
            if self._data is None:
                self._data = {}

            element = line_elements.pop(0)
            if element == 'material':
                self._label = 'material'
            elif element == 'Material':
                self._key = element
            elif _isOpenScopeMarker(element):
                self._data[self._key] = _getTypeForMarker(element)
                if self._label is not None:
                    self._data[self._key]['label'] = self._label
                self._active_state = _getStateForNode(self._key, self)
            elif _isCloseScopeMarker(element):
                self._parent.setData(self._data)
                self._active_state = self._parent
                
        return line_elements


class _IndexedFaceSetState(_BaseState):
    
    def parse(self, line_elements):
        if line_elements:
            if self._data is None:
                self._data = {}

            element = line_elements.pop(0)
            if element in ['Coordinate', 'Normal', 'coordIndex']:
                self._active_state = self
                self._key = element
                if self._previous_element:
                    self._label = self._previous_element
                    self._previous_element = None
            elif _isOpenScopeMarker(element):
                self._data[self._key] = _getTypeForMarker(element)
                if self._label is not None:
                    self._data[self._key]['label'] = self._label
                    self._label = None
                self._active_state = _getStateForNode(self._key, self)
            elif _isCloseScopeMarker(element):
                self._parent.setData(self._data)
                self._active_state = self._parent
                self._key = None
            elif element:
                self._active_state = self
                self._previous_element = element
                
        return line_elements


class _ListValueState(_BaseState):

    def parse(self, line_elements):
        if line_elements:
            if self._data is None:
                self._data = {}
                
            element = line_elements.pop(0)
            if element in ['point', 'vector']:
                self._active_state = self
                self._key = element
            elif _isOpenScopeMarker(element):
                self._data[self._key] = _getTypeForMarker(element)
                if self._label is not None:
                    self._data[self._key]['label'] = self._label
                self._active_state = _getStateForNode(self._key, self)
            elif _isCloseScopeMarker(element):
                self._parent.setData(self._data)
                self._active_state = self._parent
                
        return line_elements


class _MaterialState(_BaseState):
    
    def parse(self, line_elements):
        if line_elements:
            if self._data is None:
                self._data = {}
                
            element = line_elements.pop(0)
            if element in ['ambientIntensity', 'diffuseColor', 'specularColor', 'emissiveColor', 'shininess', 'transparency']:
                self._mode = element
                self._data[element] = None
            elif _isCloseScopeMarker(element):
                self._parent.setData(self._data)
                self._active_state = self._parent
            elif element:
                value = 0.0
                try:
                    value = float(element)
                except ValueError:
                    print('Error: Could not convert element "{0}" to a float'.format(element))
                    return line_elements
                if self._mode in ['diffuseColor', 'specularColor', 'emissiveColor']:
                    if self._data[self._mode] is None:
                        self._data[self._mode] = []
                    self._data[self._mode].append(value)
                else:
                    self._data[self._mode] = value
                
        return line_elements


class _ValueState(_BaseState):
    
    def parse(self, line_elements):
        if line_elements:
            if self._data is None:
                self._data = []
            if self._mode is None:
                self._mode = []
                
            element = line_elements.pop(0)
            if _isCloseScopeMarker(element):
                if self._mode:
                    self._data.append(self._mode)
                    self._mode = []
                self._parent.setData(self._data)
                self._active_state = self._parent
            elif element:
                triple_end = False
                value = 0.0
                try:
                    if element.endswith(','):
                        triple_end = True
                        value = float(element[:-1])
                    else:
                        value = float(element)
                except ValueError:
                    print('Error: Could not convert element "{0}" to a float'.format(element))
                    return line_elements
                if triple_end:
                    self._mode.append(value)
                    self._data.append(self._mode)
                    self._mode = []
                else:
                    self._mode.append(value)
                
        return line_elements


class _CoordIndexState(_BaseState):
    
    def parse(self, line_elements):
        if line_elements:
            if self._data is None:
                self._data = []
                
            element = line_elements.pop(0)
            if _isCloseScopeMarker(element):
                self._parent.setData(self._data)
                self._active_state = self._parent
            elif element:
                value = -1
                try:
                    if element.endswith(','):
                        value = int(element[:-1])
                    else:
                        value = int(element)
                except ValueError:
                    print('Error: Could not convert element "{0}" to a float'.format(element))
                    return line_elements

                self._data.append(value)
                
        return line_elements


dummy_count = 0
class _DummyState(_BaseState):

    def parse(self, line_elements):
        if line_elements:
            global dummy_count
            element = line_elements.pop(0)
            if _isOpenScopeMarker(element):
                dummy_count += 1
                print('enter dummy', dummy_count, element)
                self._active_state = _DummyState(self)
                self._data = _getTypeForMarker(element)
            elif _isCloseScopeMarker(element):
                print('exit dummy', dummy_count, element)
                dummy_count  -= 1
#                 line_elements = [element] + line_elements
                self._active_state = self._parent
            
        return line_elements

def _getStateForNode(node, parent):
    if node == 'Appearance':
        return _AppearanceState(parent)
    elif node == 'IndexedFaceSet':
        return _IndexedFaceSetState(parent)
    elif node == 'Material':
        return _MaterialState(parent)
    elif node in ['Coordinate', 'Normal']:
        return _ListValueState(parent)
    elif node in ['point', 'vector']:
        return _ValueState(parent)
    elif node == 'coordIndex':
        return _CoordIndexState(parent)
    
    return _DummyState(parent)

def _isOpenScopeMarker(marker):
    if marker in ['{', '[']:
        return True
    
    return False


def _isCloseScopeMarker(marker):
    if marker in ['}', ']']:
        return True
    
    return False


def _getTypeForMarker(marker):
    if marker == '{':
        return {}
    elif marker == '[':
        return []


def _checkHeader(header):
    vrml, version, encoding = header.strip().split(' ')
    #VRML V2.0 utf8
    if vrml == '#VRML' and version == 'V2.0' and encoding == 'utf8':
        return True
    
    return False
        
