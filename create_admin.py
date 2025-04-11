import os
import psycopg2
import hashlib
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

def create_admin(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Insert admin user
        cur.execute('INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)',
                   (username, password_hash, True))
        conn.commit()
        print('ადმინისტრატორი წარმატებით შეიქმნა')
    except psycopg2.IntegrityError:
        print('მომხმარებელი ამ სახელით უკვე არსებობს')
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    username = input('შეიყვანეთ მომხმარებლის სახელი: ')
    password = input('შეიყვანეთ პაროლი: ')
    create_admin(username, password) 