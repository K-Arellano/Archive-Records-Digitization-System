import cv2
import os
import tensorflow as tf
import numpy as np
from app.analyzer.name_formatter import detectStudentNames
from app.analyzer.text_recognition import analyzerText, variableSetup
from app.analyzer.textFilter import filterdata
import pandas as pd

# Analyzes the layout of the image to detect horizontal and vertical bounding boxes
def layoutAnalyzer(image_cv, boxes, image_height, image_width):
    try:
        im = image_cv.copy()  # Make a copy of the input image (assuming image_cv is a numpy array)
        horiz_boxes = []  # List to store horizontal bounding boxes
        vert_boxes = []   # List to store vertical bounding boxes

        for box in boxes:
            # Extract coordinates from the box structure
            x_h, y_h = 0, int(box[0][1])  # Horizontal line starts at x=0, y determined by top-left corner y-coordinate
            x_v, y_v = int(box[0][0]), 0  # Vertical line starts at x determined by top-left corner x-coordinate, y=0
            
            # Calculate widths and heights based on box coordinates
            width_h = image_width  # Horizontal line spans the full width of the image
            width_v = int(box[2][0] - box[0][0])  # Vertical line width based on difference between top-left and top-right x-coordinates
            height_h = int(box[2][1] - box[0][1])  # Horizontal line height based on difference between top-left and bottom-left y-coordinates
            height_v = image_height  # Vertical line spans the full height of the image
            
            # Define bounding boxes in a standardized format
            # Format: [x1, y1, x2, y2]
            horiz_boxes.append([x_h, y_h, x_h + width_h, y_h + height_h])  # Horizontal bounding box
            vert_boxes.append([x_v, y_v, x_v + width_v, y_v + width_v])   # Vertical bounding box
        
        if horiz_boxes and vert_boxes:
            return {"horiz_boxes": horiz_boxes, "vert_boxes": vert_boxes}  # Return the formatted bounding boxes
        return None

    except Exception as e:
        print('layoutAnalyzer Error: ', e)

# Detects rows (horizontal lines) using TensorFlow's non-max suppression
def rowsDetector(horiz_boxes, scores, iou_threshold):
    try:
        horiz_out = tf.image.non_max_suppression( 
            horiz_boxes,
            scores,
            max_output_size = 1000,
            iou_threshold = iou_threshold,
            score_threshold = float('-inf'),
            name = None
        )

        return horiz_out # Convert to list before returning
    except Exception as e:
        print('rowsDetector Error: ',e)

# Detects columns (vertical lines) using TensorFlow's non-max suppression
def columnDetector(vert_boxes, scores, iou_threshold):
    try:
        vert_out = tf.image.non_max_suppression( 
            vert_boxes,
            scores,
            max_output_size = 1000,
            iou_threshold = iou_threshold,
            score_threshold = float('-inf'),
            name = None
        )
        
        return vert_out #Convert to list before returning
    except Exception as e:
        print('columnDetector Error: ',e)

# Computes the intersection of two bounding boxes
def intersection(box_1, box_2):
    return[box_2[0], box_1[1], box_2[2], box_1[3]]

# Computes Intersection over Union (IoU) between two bounding boxes
def iou(box_1, box_2):
    if box_1 and box_2:  # Check if both bounding boxes are valid (not None or empty)
        x_1 = max(box_1[0], box_2[0])  # Calculate the maximum x-coordinate of the intersection
        y_1 = max(box_1[1], box_2[1])  # Calculate the maximum y-coordinate of the intersection
        x_2 = min(box_1[2], box_2[2])  # Calculate the minimum x-coordinate of the intersection
        y_2 = min(box_1[3], box_2[3])  # Calculate the minimum y-coordinate of the intersection

        inter = abs(max((x_2 - x_1, 0)) * max((y_2 - y_1, 0)))  # Calculate the absolute value of intersection area
        if inter == 0:
            return 0  # If no intersection area, return 0

        box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))  # Calculate area of box_1
        box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))  # Calculate area of box_2

        return inter / float(box_1_area + box_2_area - inter)  # Calculate and return IoU (Intersection over Union)
    return None  

# Processes the output array to fetch student names
def fetchStudentList(out_array):
    try:
        empty_columns = [i for i, heading in enumerate(out_array[0]) if not heading] #detect empty table heading or duplicated columns

        for row in out_array:
            for index in sorted(empty_columns, reverse=True): 
                del row[index] #delete determine column index for each rows

        raw_names = filterdata(out_array)

        if raw_names:
            #format the raw_names into object of formatted names
            students = detectStudentNames(raw_names)
            #displayResult(raw_names, students)
            return students
        return None
    except Exception as e:
        print('fetchStudentList Error: ',e)

# Main function to analyze table data in an image
def tableDataAnalyzer(image_path):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_directory = os.path.join(script_dir, image_path)  

        if os.path.exists(file_directory):  # Check if the image file exists
            image_cv = cv2.imread(file_directory)
            output = analyzerText(file_directory)  # Perform OCR and get text output
            
            image_height = image_cv.shape[0]  # Get image height
            image_width = image_cv.shape[1]   # Get image width
            dupl_box = []  # List to store duplicate boxes

            if output:  # Check if OCR output is not empty
                ocr_result = variableSetup(output)  # Setup variables from OCR output and filter header
                boxes = ocr_result["boxes"]  # Extract bounding boxes from OCR result
                txts = ocr_result["txts"]    # Extract texts from OCR result
                scores = ocr_result["scores"]  # Extract scores from OCR result

                layout = layoutAnalyzer(image_cv, boxes, image_height, image_width)  # Analyze layout of the image

                if layout:
                    horiz_boxes = layout['horiz_boxes']  # Get horizontal bounding boxes
                    vert_boxes = layout['vert_boxes']    # Get vertical bounding boxes
                    horiz_out = rowsDetector(horiz_boxes, scores, 0.4)  # Detect rows
                    vert_out = columnDetector(vert_boxes, scores, 0.4)   # Detect columns
                    horiz_lines = np.sort(np.array(horiz_out))  # Sort and store horizontal lines
                    vert_lines = np.sort(np.array(vert_out))    # Sort and store vertical lines

                    out_array = [["" for i in range(len(vert_lines))] for j in range(len(horiz_lines))]  # Initialize output array

                    if out_array:  # Check if output array is initialized successfully
                        for i in range(len(horiz_lines)):  # Iterate over each horizontal line
                            for j in range(len(vert_lines)):  # Iterate over each vertical line
                                resultant = intersection(horiz_boxes[horiz_lines[i]], vert_boxes[vert_lines[j]])  # Compute intersection of current horizontal and vertical boxes

                                for b in range(len(boxes)):  # Iterate all boxes data
                                    the_box = [boxes[b][0][0], boxes[b][0][1], boxes[b][2][0], boxes[b][2][1]]  # Extract coordinates of current box
                                    if iou(resultant, the_box) > 0.1:  # Check if Intersection over Union (IoU) between resultant and current box is greater valid based on the threshold
                                        if b not in dupl_box:  # Ensure current box index b is not already in dupl_box
                                            out_array[i][j] = txts[b]  # Store text by cell

                        return fetchStudentList(out_array)  # Fetch and return formatted student names from output array
        return None

    except Exception as e:
        print('tableDataAnalyzer Error: ', e)  # Print error message if an exception occurs

