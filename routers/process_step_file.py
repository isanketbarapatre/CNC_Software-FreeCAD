import math
import os
from datetime import datetime
from utils.generate_json import generate_json
from utils.Utils import *

import sys
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from pathlib import Path
#
freecad_path = "C:/Program Files/FreeCAD 0.21/bin"
if freecad_path:
    sys.path.append(freecad_path)

router = APIRouter(prefix="/files")


# Pydantic model to receive input data
class InputData(BaseModel):
    filename: UploadFile
    kFector: float

@router.post("/")
def process_step_file(file: UploadFile = File(...), kFector: float = None) -> dict:
    """
    Process an uploaded STEP file.

    This function takes an uploaded STEP file, extracts geometry data, and returns processed results
    or error messages.

    Parameters:
    file (UploadFile): The uploaded STEP file.
    kFector (float): The kFector parameter.

    Returns:
    dict: A dictionary containing the processed geometry data or an error message.
    """
    # Import necessary libraries and modules
    try:
        import FreeCAD
        from FreeCAD import Base
        import Part
        import SheetMetalUnfolderCopy as smu
    except ImportError:
        print(
            "Error: FreeCAD library not found. Please check the FREECADPATH variable in the import script is correct.")
        raise ImportError("FreeCAD library not found")

    # Constants for valid content types and extensions
    valid_content_types = ["application/STEP", "application/octet-stream"]
    valid_extensions = ['st', 'step', 'stp']

    # Check file content type and extension
    file_extension = file.filename.split(".")[1]

    if file.content_type not in valid_content_types or file_extension not in valid_extensions:
        return {"error": "Invalid Content-Type. Expected 'application/STEP'."}

    # Extract filename from the uploaded file
    filename = file.filename

    # Generate a unique name for the uploaded file using the current timestamp
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
    file_path = Path("inputFiles") / unique_filename

    # Save the uploaded file to the "inputFiles" directory
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    try:
        # Read the STEP file and create a new document
        shape = Part.read(str(file_path))
        doc = FreeCAD.newDocument()
        doc.addObject("Part::Feature", "ImportedShape").Shape = shape

        # Reference face
        ref_face = get_reference_face(doc.ImportedShape, Part, Base)

        # Function to unfold the shape
        def unfold_shape():
            unfold_points = []
            bends_points = []
            error_code = 0
            unfolded_shape = None

            if len(ref_face) != 0:
                for idx in range(len(ref_face)):
                    print('{} of obj.Name matches criteria => Selecting it'.format("Face" + str(ref_face[idx])))
                    try:
                        (unfolded_shape, unfold_points, bends_points, error_code) = smu.processUnfold(kFector, doc.ImportedShape,
                                                                                        faces[ref_face[idx] - 1],
                                                                                          "Face" + str(ref_face[idx]))

                        if len(bends_points) != 0:
                            return unfolded_shape, unfold_points, bends_points, error_code
                    except Exception as e:
                        print('{} of obj.Name not matches criteria'.format("Face" + str(ref_face[idx])))
            else:
                (unfolded_shape, unfold_points, bends_points, error_code) = smu.processUnfold(kFector, doc.ImportedShape, faces[2],
                                                                              "Face" + str(3))

            return unfolded_shape, unfold_points, bends_points, error_code

        # List of Faces
        faces = doc.ImportedShape.Shape.Faces

        # find_holes(doc.ImportedShape.Shape, Part)
        unfolded_shape, unfold_points, bends_points, error_code = unfold_shape()
        bbox = unfolded_shape.BoundBox

        # Create dictionaries for start and end points
        start_points = {'x': "{:.2f}".format(bbox.XMin), 'y': "{:.2f}".format(bbox.YMin)}
        end_points = {'x': "{:.2f}".format(bbox.XMax), 'y': "{:.2f}".format(bbox.YMax)}

        if error_code == 3:
            return {"error": "Invalid k-fector"}

        if len(bends_points) > 0:
            # Convert data to Point objects
            points = [[item[0], item[1]["vector"]] for item in unfold_points[:-len(bends_points)] if
                      item[1]["type"] == "line"]

            # Rearrange the points into a closed loop
            try:
                unfold_points, bends_points = optimize_bends_info(bends_points, points)
            except Exception as e:
                return {"error": "Unable to optimize bends"}
        else:
            points = [[item[0], item[1]["vector"]] for item in unfold_points if item[1]["type"] == "line"]
            unfold_points = points

        try:
            points, shapes, bends = extract_geometry_points(unfold_points, bends_points)
        except Exception as e:
            return {"error": "Unable to extract points"}

        json_data = generate_json(filename, 'Generated by PEdit', '', '', [start_points, end_points], points, shapes, [],
                                  bends, [], [])

        # Remove the temporary file
        file_path.unlink()
        return json_data

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}



