from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.secure.authorization import admin_required
from app.benchmark.accuracyChecker import benchmarkerTest
from app.benchmark.benchmark import updateCSV
from app.secure.randomizer import randomChar

benchmark_manager = Blueprint('benchmark_manager', __name__,url_prefix='/admin/benchmark-manager/manage')

@benchmark_manager.route('/test_ocr/accuracy', methods=['POST', 'GET'])
@login_required
@admin_required
def testErrorRate():
    try:
        data = request.get_json()
        # Extract corrected_data and ocr_data from the JSON
        corrected_data = data.get('corrected_data')
        ocr_data = data.get('ocr_data')
        result = benchmarkerTest(corrected_data, ocr_data)
        
        if result:
            return jsonify(result)
        return None
    except Exception as e:
        print(f"Failed to reconnect: {e}")

@benchmark_manager.route('/bench_result/save-data', methods=['POST', 'GET'])
@login_required
@admin_required
def saveBench():
    try:
        data = request.get_json()
        # Extract corrected_data and ocr_data from the JSON
        no_items = data.get('items')
        scantype = data.get('scantype')
        scanSpeed = data.get('scannerTime')
        WER_data = data.get('averageWER')
        CER_data = data.get('averageCER')
        benchID = randomChar(16)
        filename = "test.csv"

        if data:
            return jsonify(updateCSV(benchID, scantype, WER_data, CER_data, no_items, scanSpeed, filename))
        
        return jsonify({"update_status":"failed"})
    except Exception as e:
        print(f"Failed to reconnect: {e}")