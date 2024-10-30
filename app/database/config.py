import pymysql

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'ards_archives'

conn = pymysql.connect(host = DB_HOST, user = DB_USER, password = DB_PASSWORD, database = DB_NAME, cursorclass=pymysql.cursors.DictCursor)
