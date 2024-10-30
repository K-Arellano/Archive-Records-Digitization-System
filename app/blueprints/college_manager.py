from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.database import config
from app.secure.authorization import admin_required
from app.dynamic.source_updater import updater

college_manager = Blueprint('college_manager', __name__,url_prefix='/admin/colleges/manage/data')

from app.database import config 

class Colleges:
    def __init__(self, college_id, college_name, college_description, courses):
        self.college_id = college_id
        self.college_name = college_name
        self.college_description = college_description
        self.courses = courses

# function fetches a list of colleges from the database
def fetch_collegeList(search_college):
    try:
        if search_college:
            with config.conn.cursor() as cursor:
                #fetchall colleges in the database
                if search_college == 'all':
                    cursor.execute('SELECT college_id, college_name, college_description FROM college WHERE 1=1')
                    college_data = cursor.fetchall()
                else:
                    college_id = int(search_college)
                    cursor.execute('SELECT college_id, college_name, college_description FROM college WHERE college_id = %s', (college_id))
                    college_data = cursor.fetchall()

                if college_data:
                    return college_data
                else:
                    return None
        else:
            return None
    except Exception as e:
        print(f"fetch_collegeList error occurred: {e}")

# function fetches the courses for each college and prepares the data for display
def fetch_course(search):
     #list to store this data
    try:
        college_list = fetch_collegeList(search) #utilize the fetch colleges function
        Col_Course_list = []
        # Proceed if college list is not empty
        if college_list:
            with config.conn.cursor() as cursor: 
                # Iterate over each college
                for college_item in college_list:
                    col_id = college_item.get('college_id')
                    col_name = college_item.get('college_name')
                    col_description = college_item.get('college_description')
                    
                    # Execute SQL query to fetch courses for the current college
                    cursor.execute('SELECT course_id, course_name, course_description FROM courses WHERE registered_college =%s', (col_id))
                    course_item = cursor.fetchall()
                    courses = [] #temporary array storing courses data for each college

                    # If courses data exists, format and store it
                    if course_item: 
                        # Iterate the fetched list of courses
                        for entry in course_item:
                            #setup temporary dictionary storing course data
                            course_format = {'course_id' :"", 'course_name':""}  
                            course_format['course_id'] = entry['course_id']
                            course_format['course_name'] = entry['course_name']
                            course_format['course_description'] = entry['course_description']

                            #append the dictionary in the list
                            courses.append(course_format)
                    # Create a new college object with fetched courses and append it to the list
                    college = Colleges(col_id, col_name, col_description, courses)
                    Col_Course_list.append(college)
                    
            return Col_Course_list
        else:
            return None
    except Exception as e:
        print(f"fetch_collegeList error occurred: {e}")
    
#add college function
def createCollege(college_name, college_description):
    if college_name:
        try:
            with config.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM college WHERE college_name = %s AND college_description = %s ', (college_name, college_description))
                collegeExist = cursor.fetchone()

                if not collegeExist:
                    cursor.execute('INSERT INTO college (college_name, college_description) VALUES (%s, %s)', (college_name, college_description))
                    config.conn.commit()

                    cursor.execute('SELECT * FROM college WHERE college_name = %s', (college_name))
                    query = cursor.fetchone()

                    if query:
                        updater('college_courses')
                        return 'success'
                    else:
                        return 'failed'
                else:
                    return 'duplicate'
        except Exception as e:
            print(f"Add college error occurred: {e}")
    else:
        return 'failed'

#add course function
def createCourse(addon_College, newcourse_name,  newcourse_description):
    if newcourse_name:
        try:
            with config.conn.cursor() as cursor:
                
                cursor.execute('SELECT * FROM courses WHERE course_name = %s AND course_description = %s', (newcourse_name, newcourse_description))
                course_exist = cursor.fetchone()

                college_id = int(addon_College)

                if not course_exist:
                    cursor.execute('INSERT INTO courses (course_name, course_description, registered_college) VALUES (%s, %s, %s)', (newcourse_name, newcourse_description, college_id))
                    config.conn.commit()

                    cursor.execute('SELECT * FROM courses WHERE course_name = %s AND course_description = %s', (newcourse_name, newcourse_description))
                    success = cursor.fetchone()

                    if success:
                        updater('college_courses')
                        return 'success'
                    else:
                        return 'failed'
                else:
                    return 'duplicate'
                
        except Exception as e:
            print(f"Add Courses error occurred: {e}")
    else:
        return 'failed'

#update college function
def updateCollege(college_id, college_name, college_description, courses):
    try:
        with config.conn.cursor() as cursor:
            # Update college name
            cursor.execute('UPDATE college SET college_name = %s, college_description = %s WHERE college_id = %s AND (college_name != %s OR college_description = %s)', (college_name, college_description, college_id, college_name, college_description))
            config.conn.commit()

            if cursor.rowcount > 0:
                query_result = 'success'

            course_updatedCount = 0;

            # Update course names
            for course in courses:
                course_id = course['course_id']
                new_course_name = course['course_name']
                newc_course_description = course['course_description']
                
                cursor.execute('SELECT 1 FROM courses WHERE course_id = %s AND course_name = %s AND course_description = %s', (course_id, new_course_name, newc_course_description))
                entry = cursor.fetchone()

                if not entry:
                    cursor.execute(''' UPDATE courses SET course_name = %s , course_description = %s WHERE course_id = %s AND NOT EXISTS ( SELECT 1 FROM courses WHERE course_name = %s AND course_description = %s)''', (new_course_name, newc_course_description, course_id, new_course_name, newc_course_description))
                    config.conn.commit()

                    if cursor.rowcount > 0:
                        course_updatedCount += 1
                        
                else:
                    course_updatedCount += 1

            if course_updatedCount > 0:
                updater('college_courses')
                query_result = 'success'
            else:
                query_result = 'failed'

            return query_result
        
    except Exception as e:
        print(f"Update college error occurred: {e}")
        return 'failed'

def unlink_courseitemCollege(course, newCollege):
    course = int(course)
    newCollege = int(newCollege)

    try:
        with config.conn.cursor() as cursor:
            cursor.execute('UPDATE courses SET registered_college = %s WHERE course_id = %s', (newCollege, course))
            config.conn.commit()

            cursor.execute('SELECT * FROM courses WHERE course_id = %s AND registered_college = %s', (course, newCollege))
            isMoved = cursor.fetchone()

            if isMoved:
                updater('college_courses')
                query_result = 'success'
            else:
                query_result = 'failed'

            return query_result
        
    except Exception as e:
        print(f"Update college error occurred: {e}")
        return 'failed'

#remove college function
def removeCollege(college_id):
    if college_id:
        with config.conn.cursor() as cursor:

            cursor.execute(''' DELETE c FROM college c LEFT JOIN documents d ON c.college_id = d.college WHERE c.college_id = %s AND d.college IS NULL; ''', (college_id,))
            config.conn.commit()

            cursor.execute('SELECT * FROM college WHERE college_id = %s', (college_id))
            isDeleted = cursor.fetchone()

            if not isDeleted:
                updater('college_courses')
                query_result = 'success'
            else:
                query_result = 'cannot delete data'

        return query_result
    else:
        return 'failed'

#remove course function
def removeCourse(course_id):
    if course_id:
        with config.conn.cursor() as cursor:

            cursor.execute(''' DELETE c FROM courses c LEFT JOIN documents d ON c.course_id = d.course WHERE c.course_id = %s AND d.course IS NULL; ''', (course_id,))
            config.conn.commit()

            cursor.execute('SELECT * FROM courses WHERE course_id = %s', (course_id))
            isDeleted = cursor.fetchone()

            if not isDeleted:
                updater('college_courses')
                query_result = 'success'
            else:
                query_result = 'cannot delete data'

        return query_result
    else:
        return 'failed'

#setup route to fetch college and couses data to populate
@college_manager.route('/fetch-colleges/courses-list' , methods=['GET'])
@login_required
@admin_required
def display_colcourse():
    collegeCourses_list = fetch_course('all')
    #each entry in the collgeCourses_list is collgeCourses_list[{college_id:'', college_name:'' courses[{1, course_id:'course_id',course_name:'course_name',}]}]
    return jsonify([college.__dict__ for college in collegeCourses_list])

#setup route to regiter new college 
@college_manager.route('/add/register-data', methods=['POST', 'GET'])
@login_required
@admin_required
def create_college():
    if request.method == "POST":
        newcollege_abbrev = request.form.get('newcollege_abbrev')
        newcollege_name = request.form.get('newcollege_name')
        query_result = createCollege(newcollege_abbrev, newcollege_name)

        if query_result:
            return jsonify({'query_result' : query_result})
        else:
            return jsonify({'query_result' : 'failed'})

#setup route ot register a course entry 
@college_manager.route('/courses/append/register-data' , methods=['POST', 'GET'])
@login_required
@admin_required
def create_courses():
    if request.method == "POST":
        addon_College = request.form.get('addon_College')
        newcourse_abbrev = request.form.get('newcourse_abbrev')
        newcourse_name = request.form.get('newcourse_name')

        query_result = createCourse(addon_College, newcourse_abbrev, newcourse_name)

        if query_result:
            return jsonify({'query_result' : query_result})
        else:
            return jsonify({'query_result' : 'failed'})

#setup route to update college data and courses
@college_manager.route('/college_details/courses/data-list/update' , methods=['POST', 'GET'])
@login_required
@admin_required
def update_college():
    if request.method == "POST":
        data = request.get_json()
        college_id = data.get('college_id')
        college_name = data.get('college_name')
        college_description = data.get('college_description')
        courses_data = data.get('courses_data')

        query_result = updateCollege(college_id, college_name, college_description, courses_data)

        if query_result:
            return jsonify({'query_result' : query_result})
        else:
            return jsonify({'query_result' : 'failed'})

#setup routet to change a course registered college under cetain conditions
@college_manager.route('/courses/unlink-course/move/update/register-college' , methods=['POST', 'GET'])
@login_required
@admin_required
def change_courseCollege():
    if request.method == "POST":
        course = request.form.get('moveCourse_target')
        newCollege = request.form.get('movetoCollege')

        query_result = unlink_courseitemCollege(course, newCollege)

        if query_result:
            return jsonify({'query_result' : query_result})
        else:
            return jsonify({'query_result' : 'failed'})

#setup route to remove a collge data   
@college_manager.route('/remove_data/delete_college', methods=['POST', 'GET'])
@login_required
@admin_required
def remove_college():
    if request.method == "POST":
        college_id = request.form.get('collegeID')

    if college_id:
        college_id = int(college_id)
        query_result = removeCollege(college_id)

        if query_result:
            return jsonify({'query_result' : query_result})
        else:
            return jsonify({'query_result' : 'failed'})

#setup route to remove a collge data   
@college_manager.route('/courses/remove_data/delete-course', methods=['POST', 'GET'])
@login_required
@admin_required
def remove_course():
    if request.method == "POST":
        course_id = request.form.get('courseID')

        if course_id:
            course_id = int(course_id)
            query_result = removeCourse(course_id)

            if query_result:
                return jsonify({'query_result' : query_result})
            
    return jsonify({'query_result' : 'failed'})