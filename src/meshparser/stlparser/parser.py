'''
Created on Oct 21, 2015

@author: hsorby
'''
from zipfile import ZipFile, is_zipfile

import struct

from meshparser.base.parser import BaseParser


class STLParser(BaseParser):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super(STLParser, self).__init__()

    def canParse(self, filename):
        parseable = False
        if is_zipfile(filename):
            with ZipFile(filename) as stlzip:
                zipinfolist = stlzip.infolist()
                if len(zipinfolist) != 1:
                    print('More than one file in archive ... exiting')
                    return
                zipinfo = zipinfolist[0]
                data = stlzip.read(zipinfo.filename)
                if 'solid' in data[:80].decode("utf-8"):
                    parseable = True
        else:
            parseable = _is_ascii_stl(filename)

        return parseable

    def parse(self, filename):
        self._clear()
        if is_zipfile(filename):
            with ZipFile(filename) as stlzip:
                zipinfolist = stlzip.infolist()
                if len(zipinfolist) != 1:
                    print('More than one file in archive ... exiting')
                    return 
                zipinfo = zipinfolist[0]
                data = stlzip.read(zipinfo.filename)
                if 'solid' in data[:80].decode("utf-8"):
                    lines = data.decode("utf-8").split('\n')
                    self._parseASCII(lines)
                else:
                    self._parseBinary(data)
        elif _is_ascii_stl(filename):
            with open(filename) as f:
                lines = f.readlines()
                self._parseASCII(lines)
        else:
            with open(filename, 'rb') as f:
                data = f.read()
                self._parseBinary(data)

    def _parseASCII(self, lines):
        lines.pop(0) # Remove header line
        lines.pop() # remove endsolid
        for line in lines:
            line = line.strip()
            if line.startswith('facet'):
                node_indexes = []
            elif line.startswith('endfacet'):
                self._elements.append(node_indexes)
            elif line.startswith('vertex'):
                components = [v for v in line.split(' ') if v]
                if len(components) == 4:
                    pt = [float(components[1]), float(components[2]), float(components[3])]
                    node_indexes.append(len(self._points))
                    self._points.append(pt)
                else:
                    raise(Execption('Invalid vertex specified.'))

    def _parseBinary(self, data):
        start_byte = 0
        end_byte = 80
        _ = data[start_byte:end_byte] # header data
        start_byte = end_byte
        end_byte += 4
        facet_count = struct.unpack('I', data[start_byte:end_byte])[0]
        for _ in range(facet_count):
            start_byte = end_byte
            end_byte = start_byte + 50
            element_info = struct.unpack('ffffffffffffH', data[start_byte:end_byte])
            pt1 = [element_info[3], element_info[4], element_info[5]]
            pt1_index = len(self._points)
            self._points.append(pt1)
            pt2 = [element_info[6], element_info[7], element_info[8]]
            pt2_index = len(self._points)
            self._points.append(pt2)
            pt3 = [element_info[9], element_info[10], element_info[11]]
            pt3_index = len(self._points)
            self._points.append(pt3)

            self._elements.append([pt1_index, pt2_index, pt3_index])


class _RootState(object):
    pass

def _is_ascii_stl(filename):
    is_ascii = False
    with open(filename, 'rb') as f:
        first_bytes = f.read(80)
        if 'solid' in first_bytes.decode("utf-8").lower():
            is_ascii = True

    return is_ascii

