from flask import Blueprint, request, jsonify, Response
from flask_login import login_required
import base64
from app.database import config
from app.tools.filesize_selector import filesize_format
from app.secure.authorization import admin_required

trashbin_data = Blueprint('trashbin', __name__, url_prefix='/admin/trash/manage/data')
    
def checkDuplicateFile(document_id):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM documents WHERE filename = ( SELECT filename FROM documents WHERE docs_id = %s ) AND delete_status = 0', (document_id))
            result = cursor.fetchone()

            if result:
                return int(result['docs_id'])
        
            return None
    except Exception as e:
        print('Check Duplicate Filename Error:', e)

def checkDuplicateTags(tagging_id):
    try:
        if tagging_id:
            with config.conn.cursor() as cursor:

                cursor.execute('''SELECT * FROM tagging WHERE tag_id != %s AND delete_status = 0
                               AND student = (SELECT student FROM tagging WHERE tag_id = %s) 
                               AND document = (SELECT document FROM tagging WHERE tag_id = %s)''',  (tagging_id , tagging_id ,tagging_id))
                result = cursor.fetchone()

                if result:
                    return int(result['tag_id'])

                return False
        return None
    except Exception as e:
        print('Check Duplicate Student tags Error:', e)

def fetchTags(document_id):
    try:
        with config.conn.cursor() as cursor:
          
            cursor.execute('SELECT student FROM tagging WHERE document = %s AND delete_status = 0', (document_id))
            result = cursor.fetchall()
                
            if result:
                return result
        
        return None
    except Exception as e:
        print('fetchTags Error:', e)

def restoreVersion(inactiveFile, activeFile):
    try:
        with config.conn.cursor() as cursor:

            cursor.execute('DELETE FROM documents WHERE docs_id = %s', (activeFile,)) 
            config.conn.commit()

            if cursor.rowcount > 0:
                cursor.execute('UPDATE documents SET delete_status = 0 WHERE docs_id = %s', (inactiveFile,)) 
                config.conn.commit()
                return 'success'

            return 'failed'
    except Exception as e:
            print('Recover data Error: ',e)

def restoreAsCopy(inactiveFile, activeFile):
    try:
        with config.conn.cursor() as cursor:
            activeFile = checkDuplicateFile(activeFile)

            if cursor.rowcount > 0:
                cursor.execute("UPDATE documents SET filename = CONCAT(filename, '-copy'), delete_status = 0 WHERE docs_id = %s", (inactiveFile,))
                config.conn.commit()
                return 'success'

            return 'failed'
    except Exception as e:
            print('Recover Copy Error: ',e)

def restoreMerge(inactiveFile, activeFile):
    try:
        with config.conn.cursor() as cursor:
            trashed_tags = fetchTags(inactiveFile)
            active_tags = fetchTags(activeFile)

            if len(active_tags)> 0 and len(trashed_tags)> 0:
                inactive_list = {item['student']: item for item in active_tags}
                tagging = []

                for active_tags in trashed_tags:
                    inactive = active_tags['student']

                    if inactive in inactive_list:
                        del inactive_list[inactive]

                if len(inactive_list)  > 0:
                    for entry in inactive_list:
                        cursor.execute('INSERT INTO tagging (student, document) VALUES (%s, %s)', (entry, activeFile))
                        config.conn.commit()
                        tagging.append(cursor.lastrowid)

                    if len(tagging) > 0:
                        cursor.execute('DELETE FROM documents WHERE docs_id = %s', (inactiveFile,)) 
                        config.conn.commit()

                        return 'success'
                    else:
                        return 'failed'
                    
                return 'noChanges'
            return 'empty'
    except Exception as e:
        print('Recover Merge Error: ', e)
        return 'failed'

# This will restore the record and update the existing record with the same details, including merging linked items.    
def restoreActionType(reference_document, restore_selector):
    try:
        activeFile = checkDuplicateFile(reference_document)

        print(reference_document, restore_selector)

        if activeFile and restore_selector:
            match restore_selector:
                case 'restore-version': # Restore will delete new version to restore trashed version
                    return restoreVersion(reference_document, activeFile)
                case 'restore-merge': # Restore will merge records tags
                    return restoreMerge(reference_document, activeFile)
                case 'restore-copy': # Restore will merge records tags
                    return restoreAsCopy(reference_document, activeFile)
                
        return 'error'
    except Exception as e:
            print('Recover default Error: ',e)

def restoreDocumentFile(document_id):
    try:
        with config.conn.cursor() as cursor:

            if not checkDuplicateFile(document_id):
                cursor.execute('UPDATE documents SET delete_status = 0 WHERE docs_id = %s', (document_id,)) 
                config.conn.commit()

                if cursor.rowcount > 0:
                    return 'success'
            else:
                return 'duplicate'
            
            return 'failed'
    except Exception as e:
            print('Recover data Error: ',e)

def deleteDocumentFile(document_id):
    try:
        with config.conn.cursor() as cursor:

            cursor.execute('DELETE FROM documents WHERE docs_id = %s', (document_id,)) 
            rows_deleted = cursor.rowcount  # Get the number of affected rows
            config.conn.commit()

            if rows_deleted > 0:
                    cursor.execute('DELETE FROM trashdocs WHERE document_id = %s', (document_id))
                    config.conn.commit()

                    return 'success'

            return 'failed'
        
    except Exception as e:
            print('Recover data Error: ',e)

def restoreRecord(tagging_id):
    try:
        with config.conn.cursor() as cursor:

            if not checkDuplicateTags(tagging_id):
                cursor.execute('UPDATE tagging SET delete_status = 0 WHERE tag_id = %s', (tagging_id,)) 
                config.conn.commit()

                if cursor.rowcount > 0:
                    return 'success'
            else:
                return 'duplicate'
            
            return 'failed'
    except Exception as e:
            print('Recover data Error: ',e)

def deleteRecord(tagging_id):
    try:
        with config.conn.cursor() as cursor:

            cursor.execute('DELETE FROM tagging WHERE tag_id = %s', (tagging_id,)) 
            rows_deleted = cursor.rowcount  # Get the number of affected rows
            config.conn.commit()

            if rows_deleted > 0:
                    cursor.execute('DELETE FROM trashrecords WHERE records_id = %s', (tagging_id))
                    config.conn.commit()

                    return 'success'

            return 'failed'
        
    except Exception as e:
            print('Recover data Error: ',e)

#fetch trash data for datatable
@trashbin_data.route("/fetch-data/deleted-files/trash-list",methods=["POST","GET"])
@login_required
@admin_required
def fileRecycleBin():
    try:
        if request.method == 'POST':
            draw = request.form.get('draw') 
            row = int(request.form.get('start'))
            rowperpage = int(request.form.get('length'))
            column_index = request.form.get('order[0][column]') # Column index
            column_name = request.form.get('columns['+column_index+'][data]') # Column name
            column_sort_order = request.form.get('order[0][dir]') # asc or desc

            filterSearch = request.form.get('filterSearch')
            
            search_query = ""

            if filterSearch:
                search_terms = filterSearch.split(' ')
                for term in search_terms:
                    search_query += f" and (Filename like '%{term}%' or College like '%{term}%' or Course like '%{term}%' or Subject like '%{term}%' or SchoolYear like '%{term}%' or Semester like '%{term}%' or Unit like '%{term}%') "
            
            with config.conn.cursor() as cursor:
                # Total number of records without filtering
                cursor.execute("SELECT count(*) as allcount from trashtbl")
                records = cursor.fetchone()
                total_records = records['allcount']

                # Total number of records with filtering
                cursor.execute(f"SELECT count(*) as allcount from trashtbl WHERE 1 {search_query}")
                records = cursor.fetchone()
                total_record_with_filter = records['allcount']

                # Fetch records
                if rowperpage == -1:  # If length is -1, then it's "All"
                    stud_query = f"SELECT * FROM trashtbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()
                # limite records
                else:
                    stud_query = f"SELECT * FROM trashtbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order} LIMIT {row},{rowperpage}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()

                data = []
                if recordlist:
                    for row in recordlist:
                        
                        data.append({
                            'id': row['id'],
                            'Filename': row['Filename'],
                            'College': row['College'],
                            'Section': row['Course'] + '-' +  row['Section'],
                            'Subject': row['Subject'],
                            'Unit': row['Unit'],
                            'Semester': row['Semester'],
                            'SchoolYear': row['SchoolYear'],
                            'studentCount': row['studentCount'],
                            'page_num': row['page_num'],
                            'Trash_date': row['Trash_date'].strftime('%b %d, %Y'),
                            'editor': row['editor'],
                            'image_id': row['image_id'],
                            'File_size': filesize_format(row['Filesize']),
                        })
                    
                response = {
                    'draw': draw,
                    'iTotalRecords': total_records,
                    'iTotalDisplayRecords': total_record_with_filter,
                    'aaData': data,
                }

                return jsonify(response)
    except Exception as e:
        print('Fetch documents Error: ',e)

#fetch trash data for datatable
@trashbin_data.route("/fetch-data/deleted-tags-entries/trash-list",methods=["POST","GET"])
@login_required
@admin_required
def tagsRecycleBin():
    try:
        if request.method == 'POST':
            draw = request.form.get('draw') 
            row = int(request.form.get('start'))
            rowperpage = int(request.form.get('length'))
            column_index = request.form.get('order[0][column]') # Column index
            column_name = request.form.get('columns['+column_index+'][data]') # Column name
            column_sort_order = request.form.get('order[0][dir]') # asc or desc

            filterSearch = request.form.get('filterSearch')
            
            search_query = ""

            if filterSearch:
                search_terms = filterSearch.split(' ')
                for term in search_terms:
                    search_query += f" and (FullName like '%{term}%' or Filename like '%{term}%' or College like '%{term}%' or Course like '%{term}%' or Subject like '%{term}%' or SchoolYear like '%{term}%' or Semester like '%{term}%' or Unit like '%{term}%') "

            with config.conn.cursor() as cursor:
                # Total number of records without filtering
                cursor.execute("SELECT count(*) as allcount from tags_trashtbl")
                records = cursor.fetchone()
                total_records = records['allcount']

                # Total number of records with filtering
                cursor.execute(f"SELECT count(*) as allcount from tags_trashtbl WHERE 1 {search_query}")
                records = cursor.fetchone()
                total_record_with_filter = records['allcount']

                # Fetch records
                if rowperpage == -1:  # If length is -1, then it's "All"
                    stud_query = f"SELECT * FROM tags_trashtbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()
                # limite records
                else:
                    stud_query = f"SELECT * FROM tags_trashtbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order} LIMIT {row},{rowperpage}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()

                data = []
                if recordlist:
                    for row in recordlist:
                        
                        data.append({
                            'id': row['id'],
                            'FullName': row['FullName'],
                            'Filename': row['Filename'],
                            'College': row['College'],
                            'Section': row['Course'] + '-' +  row['Section'],
                            'Subject': row['Subject'],
                            'Unit': row['Unit'],
                            'Semester': row['Semester'],
                            'SchoolYear': row['SchoolYear'],
                            'Trash_date': row['Trash_date'].strftime('%b %d, %Y'),
                            'editor': row['editor'],
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
        print('Fetch documents Error: ',e)

#preview document image
@trashbin_data.route('/file/fetch_data/<image_id>', methods=['POST', 'GET'])
@login_required
@admin_required
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

#restore file
@trashbin_data.route('/file-list/item-document/restore-file', methods=['POST', 'GET'])
@login_required
@admin_required
def restoreFile():
    if request.method == "POST":
        document_id = request.form.get('item_id')
        document_id = int(document_id)
        recover_query = restoreDocumentFile(document_id)

        if recover_query:
            return jsonify({'recover_query': recover_query})

#custom restore file
@trashbin_data.route('/file-list/item-document/restore-custom/restore-file', methods=['POST', 'GET'])
@login_required
@admin_required
def advance_restoreFile():
    if request.method == "POST":
        document_id = request.form.get('inactive_file')
        selector = request.form.get('option')
        document_id = int(document_id)

        if selector == 'restore-default':
            recover_query = restoreDocumentFile(document_id)
        else:
            recover_query = restoreActionType(document_id, selector)

        if recover_query:
            return jsonify({'recover_query': recover_query})
        
#permanent delete one item
@trashbin_data.route('/file-list/item-document/push-delete-permanent', methods=['POST', 'GET'])
@login_required
@admin_required
def permanent_deletion():
    if request.method == "POST":
        document_id = request.form.get('item_id')
        document_id = int(document_id)
        delete_query = deleteDocumentFile(document_id)

        if delete_query:
            return jsonify({'delete_query': delete_query})

#restore file
@trashbin_data.route('/document/tags-list/restore-records', methods=['POST', 'GET'])
@login_required
@admin_required
def restoreTags():
    if request.method == "POST":
        record_id = request.form.get('item_id')
        record_id = int(record_id)
        recover_query = restoreRecord(record_id)
        
        if recover_query:
            return jsonify({'recover_query': recover_query})

#permanent delete one item
@trashbin_data.route('/document/tags-list/push-delete-permanent', methods=['POST', 'GET'])
@login_required
@admin_required
def permanent_deletion_tags():
    if request.method == "POST":
        record_id = request.form.get('item_id')
        record_id = int(record_id)
        delete_query = deleteRecord(record_id)

        if delete_query:
            return jsonify({'delete_query': delete_query})

#clear all trashed data 
@trashbin_data.route('/all-document/clear-trashbin/push-delete-permanent', methods=['POST', 'GET'])
@login_required
@admin_required
def clear_trashbin():
    try:
        if request.method == "POST":
            randomString = request.form.get('value')

            if randomString:
                with config.conn.cursor() as cursor:
                    cursor.execute('''DELETE documents FROM documents INNER JOIN trashdocs ON documents.docs_id = trashdocs.document_id''')
                    rows_deleted = cursor.rowcount
                    config.conn.commit()

                    if rows_deleted > 0:
                        delete_query = 'success'
                    else:
                        delete_query = 'failed'

                    return jsonify({'delete_query': delete_query})
    except Exception as e:
            print('clear trashbin Error: ',e)