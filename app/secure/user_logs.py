from app.database import config

#account history login
def loginHistory(user_id, session_data):
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM login_history WHERE session_data = %s AND user_id = %s', (session_data, user_id))
        current_history = cursor.fetchone()

        if not current_history:
            cursor.execute('INSERT INTO login_history (user_id, session_data) VALUES (%s, %s)',
                           (user_id, session_data))
            config.conn.commit()

def updateDB():
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('DELETE FROM user WHERE user_id IN (SELECT user_id FROM removed_sched_deact WHERE DATEDIFF(NOW(), removed_date) > 30)')
            config.conn.commit()
            print('Updating DB')
            
    except Exception as e:
        print(f"Error during database operation: {e}")
        config.conn.rollback()
