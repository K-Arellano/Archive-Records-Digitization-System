from flask import current_app as app
from flask import Blueprint, request, jsonify
from flask_login import current_user
from flask_login import login_required
from app.analyzer.detectTable import CropTable
from app.analyzer.tableRecognition import tableDataAnalyzer
import hashlib
import re
import os

ocr_App = Blueprint('ocr', __name__)

class StudentNames:
    def __init__(self, surname, firstname, middlename, suffix):
        self.surname = surname if surname else ''
        self.firstname = firstname if firstname else ''
        self.middlename = middlename if middlename else ''
        self.suffix = suffix if suffix else ''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def hashName(input_string):
    hash_object = hashlib.sha256(input_string.encode('utf-8'))
    hex_digest = hash_object.hexdigest()
    alphanumeric_digest = re.sub(r'[^a-zA-Z0-9]', '', hex_digest)
    return alphanumeric_digest[:32]

def deleteFile(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print("Deleted")
        else:
            print("Not Exist")
    except Exception as e:
        print('Deleting File Error :', e)

@ocr_App.route('/scanner/auto/<auto>', methods=['POST'])
@login_required
def scanner(auto):
    filenameCrop = hashName(current_user.id) + ".jpg"  
    image_path = "./app/analyzer/" + filenameCrop

    if 'document_image' not in request.files:
        return jsonify('noFile')
    
    file = request.files['document_image']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify('unsupported')
    
    if file and allowed_file(file.filename):

        try:
            if auto == "true":
                print("auto-scan")
                if CropTable(file, filenameCrop):
                    students = tableDataAnalyzer(filenameCrop)
                    
            else:
                print("manual-scan")
                file.save(image_path)
                students = tableDataAnalyzer(filenameCrop)
                
            deleteFile(image_path)
            
            if students:
                print('Names detected:',len(students))
                return jsonify([student.__dict__ for student in students])
            
            else:
                print('no list found')
                return None
            
        except Exception as e:
            return jsonify(e)
