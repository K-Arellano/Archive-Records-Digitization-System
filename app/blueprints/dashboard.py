from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.database import config
from app.dashboard.uploadProgress import get_countDaily, get_countWeekly, get_countMonthly, get_countYearly
from app.tools.filesize_selector import filesize_format
from app.secure.authorization import admin_required

dashboard_data = Blueprint('dashboard', __name__, url_prefix='/admin/dashboard/manage/data')

# calculate the increased percentage per month
def calculate_percentage_increase(initial, new):
    increase = new - initial
    percentage_increase = (increase / initial) * 100
    return f"{percentage_increase:.2f}"

# format the count value
def format_count(count):
    if count >= 500000:
        return '{:.2f} M'.format(count / 1000000)
    else:
        return '{:,}'.format(count)

# determine the time format and range to populate on the dashboard chart
def fetchData(dataToFetch, start_date):
    with config.conn.cursor() as cursor:
        if dataToFetch:
            match dataToFetch:
                case 'daily':
                    data = get_countDaily(start_date, None)
                    return data

                case 'weekly':
                    data = get_countWeekly(start_date, None)
                    return data

                case 'monthly':
                    data = get_countMonthly(start_date, None)
                    return data

                case 'yearly':
                    data = get_countYearly()
                    return data

        return None

#determine the number of increased and decreased in percentage between current and last month
def getIncreaseData():
    with config.conn.cursor() as cursor:
        # Get the current year and month
        current_date = datetime.now().date()
        current_year = current_date.year
        current_month = current_date.month

        # Calculate last month's year and month
        last_month_date = current_date - timedelta(days=current_date.day)
        last_month_year = last_month_date.year
        last_month_month = last_month_date.month

        # Get this month's document count
        cursor.execute('SELECT COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) = %s AND MONTH(Upload_date) = %s', (current_year, current_month))
        new_value = cursor.fetchone()['count']

        # Get last month's document count
        cursor.execute('SELECT COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) = %s AND MONTH(Upload_date) = %s', (last_month_year, last_month_month))
        old_value = cursor.fetchone()['count']

        # Calculate the difference
        if old_value > 0 and old_value != new_value:
            percentage_difference  = calculate_percentage_increase(old_value, new_value)
            return percentage_difference
        
        return None

# fetch data total count and storage size of the database
def getStatus_db():
    try:
        with config.conn.cursor() as cursor:

            result = {
            'documents_count': 0,
            'records_count': 0,
            'database_size': '',
            'trash_count': 0,
            'trash_size': '',
            'documents_status': 0,
            }

            result['documents_status'] = getIncreaseData() if getIncreaseData() is not None else 0
            # Get documents count
            cursor.execute('SELECT COUNT(*) AS doc_count FROM documentstbl')
            documents = cursor.fetchone()
            result['documents_count'] = format_count(documents['doc_count'] if documents['doc_count'] is not None else 0)

            # Get records count
            cursor.execute('SELECT COUNT(DISTINCT FullName) AS student_count FROM srecordstbl')
            records = cursor.fetchone()
            result['records_count'] = format_count(records['student_count'] if records['student_count'] is not None else 0)
            
            # Get trash count and size
            cursor.execute('SELECT COUNT(*) as trashCount, COALESCE(SUM(Filesize), 0) as sizes FROM trashtbl')
            trash_data = cursor.fetchone()
            result['trash_count'] = format_count(trash_data['trashCount'] if trash_data['trashCount'] is not None else 0)
            result['trash_size'] = filesize_format(trash_data['sizes'])

            # Get database size in MB
            cursor.execute("SELECT ROUND(SUM(data_length + index_length), 0) AS 'db_size' FROM information_schema.tables WHERE table_schema = 'ards_archives'")
            db = cursor.fetchone()
            result['database_size'] = filesize_format(db['db_size'])

            return result
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

#setup route to fetch data needed for the dashboard
@dashboard_data.route('/fetch/statistics-results/filtered', methods=['POST', 'GET'])
@login_required
@admin_required
def fetchdata():
    if request.method == 'POST':
        option = request.form.get('option')
        started_date_str = request.form.get('started_date')

        # Check if started_date_str is not empty and is a string
        if started_date_str:
            if isinstance(started_date_str, str):
                started_date = datetime.strptime(started_date_str, '%Y-%m-%d').date()
            else:
                started_date = started_date_str
        else:
            started_date = ''

        progress = fetchData(option, started_date)
        db_status = getStatus_db()

        data = {'progress':progress, 'db_status':db_status}

        if data:
            return jsonify(data)
        
        return None

