import math


def extract_geometry_points(vector_list, bends_info_list):
    """
    Extract geometry points, shapes, and bends information from vector and bends info lists.

    Parameters:
    - vector_list: List of vectors.
    - bends_info_list: List of bends information.

    Returns:
    A tuple containing points, shapes, and bends information.
    """

    unique_points = {}
    points = []
    shapes = []
    bends = []

    # Extract points and shapes from vector list
    for vectors in vector_list:
        for point in vectors[1][:2]:  # Iterate through the first two points
            x, y, _ = point
            key = (x, y)

            # Check if the point is not already added
            if key not in unique_points:
                unique_points[key] = len(unique_points) + 1
                points.append({"id": f"p{unique_points[key]}", "x": x, "y": y})

        p1 = unique_points[(vectors[1][0][0], vectors[1][0][1])]
        p2 = unique_points[(vectors[1][1][0], vectors[1][1][1])]

        shape = {"id": f"S{len(shapes) + 1}", "p1": f"p{p1}", "p2": f"p{p2}"}
        shapes.append(shape)

    # Extract bends information
    if len(bends_info_list) > 0:
        for b, bends_info in enumerate(bends_info_list):
            bend_info = {"id": f"B{b + 1}"}

            for edge in bends_info["edge"]:
                x, y, _ = edge[0]
                x2, y2, _ = edge[1]

                key1 = (x, y)
                key2 = (x2, y2)

                # Try to get points from unique_points, otherwise use stored "p1" and "p2"
                try:
                    p1 = "p" + str(unique_points[key1])
                    p2 = "p" + str(unique_points[key2])
                except KeyError:
                    p1 = bends_info["p1"]
                    p2 = bends_info["p2"]

                bend_info["p1"] = p1
                bend_info["p2"] = p2
                bend_info["angle"] = math.degrees(bends_info["angle"])
                bend_info["bDir"] = bends_info["bDir"]
                if (math.degrees(bends_info["angle"])) == 180:
                    bend_info["hem"] = "open"
                else:
                    bend_info["hem"] = "none"

                bends.append(bend_info)

    return points, shapes, bends

def point_on_line_segment(point, endpoint1, endpoint2):
    """
    Check if a point lies on a line segment defined by two endpoints.

    Parameters:
    - point: The point to check.
    - endpoint1: The first endpoint of the line segment.
    - endpoint2: The second endpoint of the line segment.

    Returns:
    If the point lies on the line segment, return a tuple of two line segments
    (segment1, segment2) where the point is in between endpoint1 and endpoint2.
    Otherwise, return None.
    """

    # Calculate the length of the line segment
    length_segment = math.dist(endpoint1, endpoint2)

    # Calculate the distances from the point to the endpoints
    distance_to_endpoint1 = math.dist(point, endpoint1)
    distance_to_endpoint2 = math.dist(point, endpoint2)

    # Check if the point lies on the line segment
    if math.isclose(distance_to_endpoint1 + distance_to_endpoint2, length_segment, rel_tol=1e-6):
        # Form two line segments with the point in between
        segment1 = (endpoint1, point)
        segment2 = (point, endpoint2)
        return segment1, segment2
    else:
        return None



def optimize_bends_info(bends_points, unfold_points):
    """
    Optimize bends information based on unfolding points.

    Parameters:
    - bends_points: List of bend points to be optimized.
    - unfold_points: List of unfolding points.

    Returns:
    A tuple containing the optimized unfold_points and bends_points.
    """

    # Iterate through each bend point
    for b in bends_points:
        for edge_point in b["edge"][0]:
            i = 0  # Initialize the loop variable outside the inner loop
            while i < len(unfold_points):
                # Extract vector from unfold_points[i]
                vector = unfold_points[i][1] if isinstance(unfold_points[i][1], tuple) else unfold_points[i][1]["vector"]

                # Check if the edge of the bend point does not match the vector
                if edge_point != vector:
                    is_lies = point_on_line_segment(edge_point, vector[0], vector[1])
                    is_lies1 = point_on_line_segment(edge_point, vector[1], vector[0])

                    # Check if the vector lies on the line segment
                    if is_lies or is_lies1:
                        segment1, segment2 = is_lies

                        # Update unfold_points with the split segments
                        unfold_points[i][1] = segment1
                        unfold_points.insert(i + 1, [unfold_points[i][0] + 1, segment2])

                        # Update bend points
                        b["p1"] = "p" + str(unfold_points[i][0])
                        b["p2"] = "p" + str(unfold_points[i][0] + 1)

                        # Update indices for subsequent vectors in unfold_points
                        for vector1 in unfold_points[i + 2:]:
                            vector1[0] = vector1[0] + 1

                        i += 2  # Update the loop variable to skip the newly inserted segment
                    else:
                        i += 1  # Move to the next item if no split occurs
                else:
                    unfold_points.remove(vector)
                    i += 1  # Move to the next item if the edge matches

    return unfold_points, bends_points


def get_reference_face(obj, Part, Base):
    """
    Get reference faces from the object based on specific conditions.

    Parameters:
    - obj: The object to analyze.
    - Part: The Part module.
    - Base: The Base module.

    Returns:
    A list of indices representing reference faces.
    """

    reference_faces = []

    # Define lower and upper boundaries
    z_min = obj.Shape.BoundBox.ZMin
    z_max = obj.Shape.BoundBox.ZMax

    # Define tolerance for distance and angle comparison
    distance_tolerance = max(1e-9 * max(abs(z_min), abs(z_max)), 0.0)
    angle_tolerance = math.pi * 1e-9

    # Define Z axis vector
    z_vector = Base.Vector(0, 0, 1)

    for i, face in enumerate(obj.Shape.Faces):
        face_type = face.Surface

        # Check if the face is a plane
        if not isinstance(face_type, Part.Plane):
            continue

        # Get face axis (normal)
        face_axis = face.Surface.Axis

        # Check if face normal is aligned with Z axis within the angle tolerance
        if abs(face_axis.getAngle(z_vector) % math.pi) > angle_tolerance:
            continue

        # Get face position on Z axis
        face_position = face.Surface.Position.z

        # Check if face is not on the boundary of the object
        if z_min + distance_tolerance < face_position < z_max - distance_tolerance:
            # Append the index of the face to the reference_faces list
            reference_faces.append(i + 1)

    # Reverse the list for consistent order
    return reference_faces[::-1]


def find_holes(obj, Part):
    """
    Find holes in the given object based on cylindrical faces with specific conditions.

    Parameters:
    - obj: The object to analyze.
    - Part: The Part module.

    Returns:
    A list containing information about the detected holes, where each element is a tuple
    (radius, center_coordinates, z_max, z_min).
    """

    # Constants
    pi_2 = 2.0 * math.pi
    eps = 0.000001

    # List to store hole information
    hole_list = []

    # Iterate through faces in the object
    for face in obj.Faces:
        # Check if the face is a cylindrical surface and meets certain parameter conditions
        if not(isinstance(face.Surface, Part.Cylinder)) or math.fabs(face.ParameterRange[0]) > eps or math.fabs(face.ParameterRange[1]-pi_2) > eps:
            continue

        surface = face.Surface

        # Check if the cylindrical axis is aligned with the Z-axis
        if math.fabs(surface.Axis.x) > eps or math.fabs(surface.Axis.y) > eps:
            continue

        # Check curvature at the center of the face
        curvature = face.curvatureAt(0, 0)
        if curvature[0] > 0 or curvature[1] > 0:
            continue

        # Add hole information to the list
        hole_list.append((surface.Radius, (surface.Center.x, surface.Center.y), face.BoundBox.ZMax, face.BoundBox.ZMin))

    return hole_list
