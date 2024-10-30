import os
import json

def settingsJson_Builder(filePath):
    # Check if the file already exists
    if os.path.exists(filePath):
        return False 
    
    # Create the file and write an empty JSON object {}
    try:
        with open(filePath, 'w') as f:
            json.dump({}, f)
        return True
    except IOError:
        return False
    
def settingsJson_loader(filename):
    script_path = os.path.dirname(os.path.abspath(__file__))  # Get current script directory
    filePath = os.path.join(script_path, "../static/json", filename)
    
    # Check if the file exists
    if os.path.exists(filePath):
        try:
            with open(filePath, 'r') as f:
                jsonFile = json.load(f)
            return jsonFile
        except json.JSONDecodeError:
            return None
    else:
        # File does not exist, call jsonSettingsBuilder to create it
        created = settingsJson_Builder(filePath)
        if created:
            # Try loading again after creation
            try:
                with open(filePath, 'r') as f:
                    jsonFile = json.load(f)
                return jsonFile
            except json.JSONDecodeError:
                return None
        else:
            return None

def json_data_selector(selector, filename):
    jsonFile = settingsJson_loader(filename)
    
    if jsonFile is None:
        return None  # Return None if JSON file couldn't be loaded
    
    if selector == "all":
        return jsonFile
    elif selector in jsonFile:
        return jsonFile[selector]
    else:
        print(f"Selector '{selector}' not found in JSON data.")
        return None

def build_CollegeCourses(college_list, courses_list):
    new_collegeData = []

    for college_item in college_list:
        college_format = {
            'college_id': college_item.get('college_id'),
            'college_name': college_item.get('college_name'),
            'college_description': college_item.get('college_description'),
            'courses': []  # Initialize an empty list for courses
        }
        
        for course_item in courses_list:
            if course_item.get('registered_college') == college_item.get('college_id'):
                course_format = {
                    'course_id': course_item.get('course_id'),
                    'course_name': course_item.get('course_name'),
                    'course_description': course_item.get('course_description')
                }
                college_format['courses'].append(course_format)

        new_collegeData.append(college_format)
    
    return new_collegeData

def build_YearLevel(academic_year):
    if academic_year and len(academic_year) > 0:
        return [{'id': year_level['id'], 'year_level': year_level['year_level'], 'description': year_level['description']} for year_level in academic_year]
    return None

def build_AcademicUnits(academic_units):
    if academic_units and len(academic_units) > 0:
        return [{'id': units_item['id'], 'unit_abbrev': units_item['unit_abbrev'], 'unit_name': units_item['unit_name']} for units_item in academic_units]
    return None

def updateSettingsJson(academic_units, academic_year, college_list, courses_list, selector):
    script_path = os.path.dirname(os.path.abspath(__file__))  # Get current script directory
    filename = "settings.json"
    filePath = os.path.join(script_path, "../static/json", filename)
    
    # Build the required data structures based on input_data
    if selector == "all":
        if academic_units and academic_year and college_list and courses_list:
            units = build_AcademicUnits(academic_units) 
            year_level = build_YearLevel(academic_year)
            college_courses = build_CollegeCourses(college_list, courses_list)
        else:
            return False
    
    elif selector == "academic_units":
        if academic_units:
            units = build_AcademicUnits(academic_units) 
        else:
            return False
    
    elif selector == "academic_year":
        if academic_year:
            year_level = build_YearLevel(academic_year)
        else:
            return False
    
    elif selector == "college_courses":
        if college_list and courses_list:
            college_courses = build_CollegeCourses(college_list, courses_list)
        else:
            return False
    
    else:
        print(f"Unsupported selector: {selector}")
        return False

    # Load existing JSON data
    jsonFile = settingsJson_loader(filename)

    if jsonFile is not None:
        if selector == "all":
            if units and year_level and college_courses:
                jsonFile.clear()
                jsonFile['units'] = units
                jsonFile['year_level'] = year_level
                jsonFile['college_courses'] = college_courses

        elif selector == "academic_units":
            if units:
                jsonFile['units'] = units

        elif selector == "academic_year":
            if year_level:
                jsonFile['year_level'] = year_level

        elif selector == "college_courses":
            if college_courses:
                jsonFile['college_courses'] = college_courses

        # Save the updated JSON back to the file
        try:
            with open(filePath, 'w') as f:
                json.dump(jsonFile, f, indent=4)  # Added indentation for readability
            return True  # Return True if successfully updated
        except Exception as e:
            print(f"Error updating JSON file: {e}")
            return False  # Return False on error

    return False  # Return False if jsonFile is None or update failed

