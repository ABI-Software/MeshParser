import struct
from zipfile import ZipFile, is_zipfile

from meshparser.base.parser import BaseParser


class STLParser(BaseParser):

    def __init__(self):
        super(STLParser, self).__init__()

    def can_parse(self, filename):
        parseable = False
        if is_zipfile(filename):
            with ZipFile(filename) as stlzip:
                zipinfolist = stlzip.infolist()
                if len(zipinfolist) == 1:
                    zipinfo = zipinfolist[0]
                    data = stlzip.read(zipinfo.filename)
                    # Try and determine if this is an ASCII zipped file or binary zipped file.
                    first_bytes = data[:90]
                    if _is_ascii_stl(first_bytes) or _is_binary_stl(first_bytes):
                        parseable = True
        else:
            with open(filename, 'rb') as f:
                first_bytes = f.read(90)
                parseable = _is_ascii_stl(first_bytes)

        return parseable

    def parse(self, filename):
        self._clear()
        if is_zipfile(filename):
            with ZipFile(filename) as stlzip:
                zipinfolist = stlzip.infolist()
                if len(zipinfolist) == 1:
                    zipinfo = zipinfolist[0]
                    data = stlzip.read(zipinfo.filename)
                    first_bytes = data[:90]
                    if _is_ascii_stl(first_bytes):
                        lines = data.decode("utf-8").split('\n')
                        self._parse_ascii(lines)
                    elif _is_binary_stl(first_bytes):
                        self._parse_binary(data)
        else:
            bin_parseable = False
            with open(filename, 'rb') as f:
                first_bytes = f.read(90)
                ascii_parseable = _is_ascii_stl(first_bytes)
                if not ascii_parseable:
                    bin_parseable = _is_binary_stl(first_bytes)

            if ascii_parseable:
                with open(filename) as f:
                    lines = f.readlines()
                    self._parse_ascii(lines)
            elif bin_parseable:
                with open(filename, 'rb') as f:
                    data = f.read()
                    self._parse_binary(data)

    def _parse_ascii(self, lines):
        node_indexes = None
        lines.pop(0) # Remove header line
        lines.pop() # remove end solid
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
                    raise(Exception('Invalid vertex specified.'))

    def _parse_binary(self, data):
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


def _is_ascii_stl(first_bytes):
    """
    Determine if this is an ASCII based data stream, simply by checking the bytes for the word 'solid'.
    """
    is_ascii = False
    if 'solid' in first_bytes.decode("utf-8").lower():
        is_ascii = True

    return is_ascii


def _is_binary_stl(data):
    """
    Determine if this is a binary file through unpacking the first value after the 80th character
    and testing whether this value is greater than zero.  This indicates the number of facets in the file.
    Could possibly extend this to check that the remaining number of bytes is divisible by 50.
    """
    is_bin = False
    start_byte = 0
    end_byte = 80
    _ = data[start_byte:end_byte] # header data
    start_byte = end_byte
    end_byte += 4
    facet_count = struct.unpack('I', data[start_byte:end_byte])[0]
    if facet_count > 0:
        is_bin = True

    return is_bin

