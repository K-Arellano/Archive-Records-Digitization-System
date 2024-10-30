from flask import Blueprint, request, jsonify, Response
from flask_login import login_required, current_user
import base64
from app.database import config
from app.secure.authorization import authenticate

fetch_records = Blueprint('fetch_records', __name__, url_prefix='/documents/records/tags/manage/data')

def getEditor():
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM user WHERE username = %s', (current_user.username))
        account_uploader = cursor.fetchone()

        if account_uploader:
            editor = account_uploader['user_id']
            return editor
        else:
            return None
        
# fetch the student credentials fo edit
def fetchEntryData(tag_id):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute(""" SELECT students.*, tagging.*, documents.docs_id FROM students JOIN tagging ON students.student_id = tagging.student JOIN documents ON tagging.document = documents.docs_id WHERE tagging.tag_id = %s """, (tag_id,))
            student_data = cursor.fetchone()

            record_data = { 'surname': '', 'firstname': '', 'middlename': '', 'suffix': '', 'document': ''}
            record_data['surname'] = student_data['surname']
            record_data['firstname'] = student_data['firstname']
            record_data['middlename'] = student_data['middlename']
            record_data['suffix'] = student_data['suffix']
            record_data['document'] = student_data['docs_id']

            return record_data

    except Exception as e:
        print('Fetch Recordds Error :', e)

def checkDuplicateTags(document_id, student_id):
    try:
        if document_id and student_id:

            with config.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM tagging WHERE student = %s AND document = %s', 
                               (student_id, document_id))
                tagExist = cursor.fetchone()

                if tagExist:
                    return True

                return False
        return None
    except Exception as e:
        print('Check Duplicate Student tags Error:', e)

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

# update the tagged student information/credentials
def editRecordsData(tagging_id, document_id, new_surname, new_firstname, new_middlename, new_suffix):
    try:
        with config.conn.cursor() as cursor:

            if tagging_id and document_id:
                tagging_id = int(tagging_id)
                document_id = int(document_id)
                
                cursor.execute('SELECT * FROM students WHERE surname = %s AND firstname = %s AND middlename = %s AND suffix = %s', (new_surname, new_firstname, new_middlename, new_suffix))
                student_exist = cursor.fetchone()

                student_id = student_exist['student_id'] if student_exist else newStudent(new_surname, new_firstname, new_middlename, new_suffix)
                
                if student_id:
                    if checkDuplicateTags(document_id, student_id) == True and student_id:
                        return 'duplicate'
                    else:
                        cursor.execute('UPDATE tagging SET student =%s , delete_status = 0 WHERE tag_id = %s', (student_id, tagging_id))
                        config.conn.commit()

                        if cursor.rowcount > 0:
                                return 'success'
                
                else:
                    return 'tagNotFound'
                       
            return 'failed'
    except Exception as e:
        print('Update Error :', e)
        return 'failed'

#remove record data 
def removeRecordData(tagging_id):
    try:
        with config.conn.cursor() as cursor:
            if tagging_id:
                tagging_id = int(tagging_id)
                editor = getEditor()

                cursor.execute('UPDATE tagging SET delete_status = 1 WHERE tag_id = %s', (tagging_id,)) 
                config.conn.commit()

                if cursor.rowcount > 0:
                    cursor.execute('INSERT INTO trashrecords (records_id, editor, trashed_date) VALUES (%s, %s, NOW())', (tagging_id, editor))
                    config.conn.commit()
                    
                    return 'success'
                
                return 'failed'
            
    except Exception as e:
        print('Remove Recordds Error :', e)

#setup route to fetch data for datatable
@fetch_records.route("/fetch/tags/students_list",methods=["POST","GET"])
@login_required
@authenticate
def records_data():
    try:
        if request.method == 'POST':
            draw = request.form.get('draw') 
            row = int(request.form.get('start'))
            rowperpage = int(request.form.get('length'))
            column_index = request.form.get('order[0][column]') # Column index
            column_name = request.form.get('columns['+column_index+'][data]') # Column name
            column_sort_order = request.form.get('order[0][dir]') # asc or desc

            filterSearch = request.form.get('filterSearch')
            filterCollege = request.form.get('filterCollege')
            filterCourse = request.form.get('filterCourse')
            filterSemester = request.form.get('filterSemester')
            filterYear = request.form.get('filterYear')

            search_query = ""

            if filterSearch:
                search_terms = filterSearch.split(' ')
                for term in search_terms:
                    search_query += f" and (FullName like '%{term}%' or College like '%{term}%' or Course like '%{term}%' or Subject like '%{term}%' or SchoolYear like '%{term}%' or Semester like '%{term}%' or Unit like '%{term}%') "
            
            if filterCollege:
                search_query += f" and (College = '{filterCollege}')"
            if filterCourse:
                search_query += f" and (Course = '{filterCourse}')"
            if filterYear:
                search_query += f" and (year_level = '{filterYear}')"
            if filterSemester:
                search_query += f" and (Semester = '{filterSemester}')"  

            with config.conn.cursor() as cursor:
                # Total number of records without filtering
                cursor.execute("SELECT count(*) as allcount from srecordstbl")
                records = cursor.fetchone()
                total_records = records['allcount']

                # Total number of records with filtering
                cursor.execute(f"SELECT count(*) as allcount from srecordstbl WHERE 1 {search_query}")
                records = cursor.fetchone()
                total_record_with_filter = records['allcount']

                # Fetch records
                if rowperpage == -1:  # If length is -1, then it's "All"
                    stud_query = f"SELECT * FROM srecordstbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()
                # limite records
                else:
                    stud_query = f"SELECT * FROM srecordstbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order} LIMIT {row},{rowperpage}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()

                data = []
                if recordlist:
                    for row in recordlist:
                        data.append({
                            'id': row['id'],
                            'FullName': row['FullName'],
                            'College': row['College'],
                            'Section': row['Course'] + '-' +  row['Section'],
                            'Subject': row['Subject'],
                            'Unit': row['Unit'],
                            'Semester': row['Semester'],
                            'SchoolYear': row['SchoolYear'],
                            'image_id': row['image_id'],
                        })
                    
                response = {
                    'draw': draw,
                    'iTotalRecords': total_records,
                    'iTotalDisplayRecords': total_record_with_filter,
                    'aaData': data,
                }

                return jsonify(response)
    except Exception as e:
        print('Fetch Records Error: ',e)

#setup route to preview document image
@fetch_records.route('/file/fetch_data/<image_id>', methods=['POST', 'GET'])
@login_required
@authenticate
def previewDocument(image_id):
    image_id = int(image_id)
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM img_files WHERE img_id = %s', image_id)
        image_data = cursor.fetchone()

        if image_data:
            document_image = image_data['document_file']
            encoded_image = base64.b64encode(document_image).decode('utf-8')
            return Response(encoded_image)
        
        return "No image data found", 404
    
#setup route to fetch tag entry student credentials
@fetch_records.route('/students/request/credentials/<tag_id>', methods=['POST', 'GET'])
@login_required
@authenticate
def getEntryData(tag_id):
    tag_id = int(tag_id)

    if tag_id:
        query_result = fetchEntryData(tag_id)
        return jsonify(query_result)
    
#setup route to edit records data   
@fetch_records.route('/students/credentials/update', methods=['POST', 'GET'])
@login_required
@authenticate
def editEntryData():
    if request.method == "POST":
        tagging_id = request.form.get('tagging_id')
        document_id = request.form.get('document_id')
        new_surname = request.form.get('update_surname') if request.form.get('update_surname') else ""
        new_firstname = request.form.get('update_firstname') if request.form.get('update_firstname') else ""
        new_middlename = request.form.get('update_middlename') if request.form.get('update_middlename') else ""
        new_suffix = request.form.get('update_suffix') if request.form.get('update_suffix') else ""

        tagging_id = int(tagging_id)
        document_id = int(document_id)

        if tagging_id:
            update_query = editRecordsData(tagging_id, document_id, new_surname, new_firstname, new_middlename, new_suffix)

            if update_query:
                return jsonify({'update_query': update_query})
        
#setup route to delete records data                
@fetch_records.route('/students/remove/unlink/update/document', methods=['POST', 'GET'])
@login_required
@authenticate
def deleteEntryData():
    if request.method == "POST":
        tagging_id = request.form.get('tagging_id')
        tagging_id = int(tagging_id)

        delete_query = removeRecordData(tagging_id)

        if delete_query:
            return jsonify({'delete_query': delete_query})
        

