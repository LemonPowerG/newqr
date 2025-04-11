import os
import psycopg2
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

def get_db_connection():
    if 'DATABASE_URL' in os.environ:
        url = urlparse(os.environ['DATABASE_URL'])
        return psycopg2.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            port=url.port
        )
    else:
        return psycopg2.connect(
            host='localhost',
            user='postgres',
            password='your-password',
            database='feedback_system'
        )

def check_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check users table
        cur.execute('SELECT COUNT(*) FROM users')
        user_count = cur.fetchone()[0]
        print(f'Users table: {user_count} records')
        
        # Check branches table
        cur.execute('SELECT COUNT(*) FROM branches')
        branch_count = cur.fetchone()[0]
        print(f'Branches table: {branch_count} records')
        
        # Check feedback table
        cur.execute('SELECT COUNT(*) FROM feedback')
        feedback_count = cur.fetchone()[0]
        print(f'Feedback table: {feedback_count} records')
        
        # Get feedback statistics
        cur.execute('''
            SELECT 
                AVG(service_rating) as avg_service,
                AVG(cleanliness_rating) as avg_cleanliness,
                AVG(staff_rating) as avg_staff,
                AVG(waiting_time_rating) as avg_waiting,
                AVG(overall_rating) as avg_overall
            FROM feedback
        ''')
        stats = cur.fetchone()
        print('\nAverage Ratings:')
        print(f'Service: {stats[0]:.2f}')
        print(f'Cleanliness: {stats[1]:.2f}')
        print(f'Staff: {stats[2]:.2f}')
        print(f'Waiting Time: {stats[3]:.2f}')
        print(f'Overall: {stats[4]:.2f}')
        
    except psycopg2.Error as e:
        print(f'Database error: {e}')
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    check_database() 