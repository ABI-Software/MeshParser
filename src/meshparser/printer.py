import math


def _calculate_normal(pt1, pt2, pt3):
    u = [pt2[0] - pt1[0], pt2[1] - pt1[1], pt2[2] - pt1[2]]
    v = [pt3[0] - pt1[0], pt3[1] - pt1[1], pt3[2] - pt1[2]]
    w = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    mag_w = math.sqrt(w[0] * w[0] + w[1] * w[1] + w[2] * w[2])
    mag_w = mag_w if mag_w > 1e-08 else 1

    return [w[i] / mag_w for i in range(3)]


class STLPrinter:

    def __init__(self, mesh, filename):
        self._mesh = mesh
        self._filename = filename

    def print(self):
        elements = self._mesh.get("elements", [])
        points = self._mesh.get("points", [])
        with open(self._filename, 'w') as stl_file:
            stl_file.write('solid\n')

            for tri in elements:
                pt1 = points[tri[0]]
                pt2 = points[tri[1]]
                pt3 = points[tri[2]]

                normal = _calculate_normal(pt1, pt2, pt3)
                stl_file.write(f' facet normal {normal[0]} {normal[1]} {normal[2]}\n')

                stl_file.write('    outer loop\n')
                for ver in [pt1, pt2, pt3]:
                    stl_file.write(f'      vertex {ver[0]} {ver[1]} {ver[2]}\n')
                stl_file.write('    endloop\n')

                stl_file.write(' endfacet\n')
            stl_file.write('endsolid\n')


def print_mesh(mesh, filename, use_printer='stl'):
    lower = use_printer.lower()
    if lower == 'stl':
        printer = STLPrinter(mesh, filename)
    else:
        raise NotImplementedError('A parser for the value: "{0}" has not been implemented.'.format(use_printer))

    printer.print()
