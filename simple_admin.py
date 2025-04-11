import os
import psycopg2
import hashlib
from urllib.parse import urlparse

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

def create_simple_admin():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if admin already exists
        cur.execute('SELECT * FROM users WHERE username = %s', ('admin',))
        admin = cur.fetchone()
        
        if admin:
            print('ადმინისტრატორი უკვე არსებობს')
            return
        
        # Create admin user
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cur.execute('INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)',
                   ('admin', password_hash, True))
        conn.commit()
        print('ადმინისტრატორი წარმატებით შეიქმნა')
        print('მომხმარებელი: admin')
        print('პაროლი: admin123')
    except psycopg2.Error as e:
        print(f'Database error: {e}')
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    create_simple_admin() 