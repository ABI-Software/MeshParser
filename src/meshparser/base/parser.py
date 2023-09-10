from pointpare import PointPare


class BaseParser(object):

    def __init__(self):
        self._points = None
        self._elements = None
        self._clear()

    def _clear(self):
        self._points = []
        self._elements = []

    def can_parse(self, filename):
        """
        Tries to determine whether this parser can parse the given filename.  May return false negatives!
        :param filename: The filename of the file to parse.
        :return: True if this parser can pass the given filename, otherwise False.
        """
        return False

    def parse(self, filename):
        raise NotImplementedError('Method "parse" not implemented')

    def get_points(self, pared=False):
        """
        Get the points that make up the mesh.
        :param pared: use the pared down list of points
        :return: A list of points
        """
        points = self._points[:]
        if pared:
            pp = PointPare()
            pp.add_points(points)
            pp.pare_points()
            points = pp.get_pared_points()

        return points

    def get_elements(self, zero_based=True, pared=False):
        """
        Get the elements of the mesh as a list of point index list.
        :param zero_based: use zero based index of points if true otherwise use 1-based index of points.
        :param pared: use the pared down list of points
        :return: A list of point index lists
        """
        points = self._points[:]
        elements = self._elements[:]
        offset = 0
        if not zero_based:
            offset = 1

        pp = None
        if pared:
            pp = PointPare()
            pp.add_points(points)
            pp.pare_points()

        if pared or not zero_based:
            modified_elements = []
            for element in elements:
                modified_element = [index + offset if pp is None else pp.get_pared_index(index) + offset
                                    for index in element]
                modified_elements.append(modified_element)

            elements = modified_elements

        return elements
