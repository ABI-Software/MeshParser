from meshparser.nodepare.pare import NodePare


class BaseParser(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._clear()

    def _clear(self):
        self._points = []
        self._elements = []

    def parse(self, filename):
        raise NotImplementedError('Method "parse" not implemented')

    def getPoints(self, pared=False):
        """
        Get the points that make up the mesh.
        :param pared: use the pared down list of points
        :return: A list of points
        """
        points = self._points[:]
        if pared:
            np = NodePare()
            np.addPoints(points)
            np.parePoints()
            points = np.getParedPoints()

        return points

    def getElements(self, zero_based=True, pared=False):
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

        np = None
        if pared:
            np = NodePare()
            np.addPoints(points)
            np.parePoints()

        if pared or not zero_based:
            modified_elements = []
            for element in elements:
                modified_element = [index + offset if np is None else np.getParedIndex(index) + offset for index in element]
                modified_elements.append(modified_element)

            elements = modified_elements

        return elements



