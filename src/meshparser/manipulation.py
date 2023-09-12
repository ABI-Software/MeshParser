import math


def translate(mesh, offset):
    points = mesh.get("points", [])
    translated_mesh = {"elements": mesh.get("elements", [])}
    translated_points = [None]*len(points)
    for index, point in enumerate(points):
        translated_points[index] = [point[i] + offset[i] for i in range(3)]

    translated_mesh["points"] = translated_points
    return translated_mesh


def rotate(mesh, axis, angle):
    points = mesh.get("points", [])
    rotated_mesh = {"elements": mesh.get("elements", [])}
    rotated_points = [None]*len(points)
    rotation_mx = _form_axis_angle_rotation_matrix(axis, angle)
    for index, point in enumerate(points):
        rotated_points[index] = [rotation_mx[i][0]*point[0] + rotation_mx[i][1]*point[1] + rotation_mx[i][2]*point[2] for i in range(3)]

    rotated_mesh["points"] = rotated_points
    return rotated_mesh


def calculate_centre_of_mass(mesh):
    elements = mesh.get("elements", [])
    points = mesh.get("points", [])
    total_area = 0.0
    area_distance = [0.0, 0.0, 0.0]
    for element in elements:
        side_length_1 = _side_length(points[element[0]], points[element[1]])
        side_length_2 = _side_length(points[element[1]], points[element[2]])
        side_length_3 = _side_length(points[element[2]], points[element[0]])
        semi_perimeter = 0.5 * (side_length_1 + side_length_2 + side_length_3)
        triangle_area = math.sqrt(semi_perimeter * (semi_perimeter - side_length_1) * (semi_perimeter - side_length_2) * (semi_perimeter - side_length_3))
        triangle_centre = _calculate_triangle_centre(points[element[0]], points[element[1]], points[element[2]])

        for i in range(3):
            area_distance[i] += (triangle_area * triangle_centre[i])
        total_area += triangle_area

    return [area_distance[i] / total_area for i in range(3)]


def _side_length(pt1, pt2):
    length = 0.0
    for i in range(3):
        diff = pt1[i] - pt2[i]
        length += diff*diff

    return math.sqrt(length)


def _calculate_triangle_centre(pt1, pt2, pt3):
    return [(pt1[i] + pt2[i] + pt3[i]) / 3 for i in range(3)]


def _form_axis_angle_rotation_matrix(axis, angle):
    angle_rad = angle / 180.0 * math.pi
    cos_phi = math.cos(angle_rad)
    sin_phi = math.sin(angle_rad)
    omcp = 1 - cos_phi
    mx_half_a = [[cos_phi, axis[2]*sin_phi, -axis[1]*sin_phi],
                 [-axis[2]*sin_phi, cos_phi, axis[0]*sin_phi],
                 [axis[1]*sin_phi, -axis[0]*sin_phi, cos_phi]]
    mx_half_b = [[axis[0]*axis[0]*omcp, axis[0]*axis[1]*omcp, axis[0]*axis[2]*omcp],
                 [axis[1]*axis[0]*omcp, axis[1]*axis[1]*omcp, axis[1]*axis[2]*omcp],
                 [axis[2]*axis[0]*omcp, axis[2]*axis[1]*omcp, axis[2]*axis[2]*omcp]]
    rot_mx = [[mx_half_a[0][0] + mx_half_b[0][0], mx_half_a[0][1] + mx_half_b[0][1], mx_half_a[0][2] + mx_half_b[0][2]],
              [mx_half_a[1][0] + mx_half_b[1][0], mx_half_a[1][1] + mx_half_b[1][1], mx_half_a[1][2] + mx_half_b[1][2]],
              [mx_half_a[2][0] + mx_half_b[2][0], mx_half_a[2][1] + mx_half_b[2][1], mx_half_a[2][2] + mx_half_b[2][2]]]

    return rot_mx
