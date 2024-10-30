from app.database import config
from app.dynamic.settings import updateSettingsJson

def fetch_college():
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM college WHERE 1=1')
        return cursor.fetchall()

def fetch_courses():
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM courses WHERE 1=1')
        return cursor.fetchall()

def fetch_units():
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM academic_units WHERE 1=1')
        return cursor.fetchall()

def fetch_year_level():
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM academic_yearLevel WHERE 1=1')
        return cursor.fetchall()
    
def updater(selector):
    college_list = []
    courses_list = []
    academic_units = []
    academic_year = []

    if selector:
        if selector == "all":
            college_list = fetch_college()
            courses_list = fetch_courses()
            academic_units = fetch_units()
            academic_year = fetch_year_level()
        
        elif selector == "academic_units":
            academic_units = fetch_units() 

        elif selector == "academic_year":
            academic_year = fetch_year_level()
        
        elif selector == "college_courses":
            college_list = fetch_college()
            courses_list = fetch_courses()
                
        result = updateSettingsJson(academic_units, academic_year, college_list, courses_list, selector)