from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flask import current_app as app
import json
from app.database import config
from app.secure.authorization import authenticate

uploader_manager = Blueprint('upload_manager', __name__,url_prefix='/archival')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def getEditor():
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM user WHERE username = %s', (current_user.username))
        account_uploader = cursor.fetchone()

        if account_uploader:
            editor = account_uploader['user_id']
            return editor
        else:
            return None

def newDocumentUploader(document_header, imageFile):
    if document_header:
        document = document_header
        filename = document.get('filename')
        college = document.get('college')
        course = document.get('course')
        year_level = document.get('yearLevel')
        section = document.get('section')
        subject_name = document.get('subject_name')
        unit = document.get('subject_type')
        semester = document.get('semester')
        academic_year = document.get('academicYear')
        document_page = document.get('document_page')

    if college != "" and course != "":
        try:
            with config.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM documents WHERE filename = %s AND delete_status = 0', (filename))
                document_exist = cursor.fetchone()

                if not document_exist:
                    editor = getEditor()
                    
                    cursor.execute('INSERT INTO documents (filename, college, course, section, subject, academic_year, semester, year_level, unit, page_num, editor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (filename, college, course, section, subject_name, academic_year, semester, year_level, unit, document_page, editor))
                    config.conn.commit()

                    document_id = cursor.lastrowid
                    
                    print(document_id)

                    if document_id:
                        image_id = imageUploader(imageFile, document_id)

                        if document_id and image_id:
                            return document_id
                        else:
                            return None
                else:
                    return None
        except Exception as e:
                print(f"Upload document error occurred: {e}")
                return e
    else:
        return None
    
def imageUploader(imageFile, document_id):
    document_image = imageFile.read()
    document_id = int(document_id)
    try:
        if document_id and document_image:

            with config.conn.cursor() as cursor:
                cursor.execute('INSERT INTO img_files (document_file, document) VALUES (%s, %s)', (document_image, document_id))
                config.conn.commit()
                uploaded = cursor.lastrowid

                return uploaded
        return None
    except Exception as e:
                print(f"Upload image error occurred: {e}")

def newStudent(entry_surname,entry_firstname, entry_middlename, entry_suffix):
    if not entry_surname and not entry_firstname:
        return None
    else:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM students WHERE surname = %s AND firstname = %s AND middlename = %s AND suffix = %s', (entry_surname, entry_firstname, entry_middlename, entry_suffix) )
            student_credentials = cursor.fetchone()

            if not student_credentials:
                cursor.execute('INSERT INTO students(surname, firstname, middlename, suffix) VALUES (%s,%s,%s,%s)', (entry_surname, entry_firstname, entry_middlename, entry_suffix))
                config.conn.commit()
                return cursor.lastrowid
            else:
                return student_credentials['student_id']

def generateLink(document_id, student_id):
    if not document_id and not student_id :
        return None
    else:
        editor = getEditor()
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM tagging WHERE document = %s AND student = %s AND delete_status = 0', (document_id, student_id))
            linked_item = cursor.fetchone()

            if not linked_item:
                cursor.execute('INSERT INTO tagging(document, student, editor) VALUES (%s,%s,%s)', (document_id, student_id, editor))
                config.conn.commit()

                return cursor.lastrowid
            else:
                return linked_item['tag_id']

def newRecordData(document_header, imageFile, students_data):
    document_id = newDocumentUploader(document_header, imageFile)
    try:
        with config.conn.cursor() as cursor:
            if document_id:
                if students_data:
                    tagging = []
                    for student in students_data:
                        entry_surname = student['student_surname']
                        entry_firstname = student['student_firstname']
                        entry_middlename = student['student_middlename']
                        entry_suffix = student['student_suffixname']
                        student_id = newStudent(entry_surname,entry_firstname, entry_middlename, entry_suffix)

                        if student_id:
                            linked = generateLink(document_id, student_id)
                            tagging.append(linked)
                    
                    if len(tagging) > 0:
                        return'success'
                    else:
                        return 'failed'
            else:
                return 'duplicate'  

    except Exception as e:
            print(f"new record error occurred: {e}")

@uploader_manager.route('/newRecord/document_upload', methods=['POST', 'GET'])
@login_required
@authenticate
def uploader():
    if 'document_image' not in request.files:
        query_result = "noFile"

    file = request.files['document_image']

    if file.filename == '' or not allowed_file(file.filename):
        query_result = "unsupported"

    if 'document_image' and allowed_file(file.filename):
        # Extract other document information
        document_filename = request.form.get('document_filename')
        document_college = request.form.get('document_college')
        document_course = request.form.get('document_course')
        document_yearLevel = request.form.get('document_yearLevel')
        course_section = request.form.get('course_section')
        document_subject_name = request.form.get('document_subject_name')
        document_subject_type = request.form.get('document_subject_type')
        document_semester = request.form.get('document_semester')
        document_academicYear = request.form.get('document_academicYear')
        document_page = request.form.get('document_page')

        document_header = {
            'filename': document_filename,
            'college': int(document_college),
            'course': int(document_course),
            'yearLevel': int(document_yearLevel),
            'section': course_section,
            'subject_name': document_subject_name,
            'subject_type': int(document_subject_type),
            'semester': int(document_semester),
            'academicYear': document_academicYear,
            'document_page': int(document_page),
        }

        students_data_str = request.form.get('studentsData')

        try:
            students_data = json.loads(students_data_str)
        except json.JSONDecodeError:
            students_data = []

        query_result = newRecordData(document_header, file, students_data)

    return jsonify({'query_result': query_result})





