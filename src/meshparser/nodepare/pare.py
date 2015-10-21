'''
Created on Oct 21, 2015

@author: hsorby
'''

class NodePare(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._paredPoints = []
        self.clearPoints()
        
    def clearPoints(self):
        self._points = []
        self._pointMap = {}
        
    def addPoint(self, point):
        self._points.append(point)
        
    def addPoints(self, points):
        self._points.extend(points)
        
    def parePoints(self):
        self._paredPoints = []
        tmp = {}
        for index, pt in enumerate(self._points):
            dim = 0
            c_prev = []
            new_point = False
            while dim < len(pt):
                c = str(pt[dim])
                if dim == 0 and c not in tmp:
                    tmp[c] = {}
                elif dim == 1 and c not in tmp[c_prev[0]]:
                    tmp[c_prev[0]][c] = {}
                elif dim == 2 and c not in tmp[c_prev[0]][c_prev[1]]:   
                    tmp[c_prev[0]][c_prev[1]] = {}
                    new_point = True
                    
                c_prev.append(c)
                dim += 1
                    
            if new_point:
                pared_index = len(self._paredPoints)
                tmp[c_prev[0]][c_prev[1]][c_prev[2]] = pared_index
                self._paredPoints.append(pt)
            else:
                pared_index = tmp[c_prev[0]][c_prev[1]][c_prev[2]]
                
            self._pointMap[index] = pared_index
    
    def getParedIndex(self, node_index):
        '''
        Return the pared node index for the original 
        node position.
        '''
        return self._pointMap[node_index]
        
    def getParedPoints(self):
        return self._paredPoints