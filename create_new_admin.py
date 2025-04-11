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

def create_new_admin(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if user already exists
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cur.fetchone()
        
        if existing_user:
            print(f'მომხმარებელი ამ სახელით უკვე არსებობს: {username}')
            return
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create new admin user
        cur.execute('INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)',
                   (username, password_hash, True))
        conn.commit()
        print(f'ახალი ადმინისტრატორი წარმატებით შეიქმნა: {username}')
    except psycopg2.Error as e:
        print(f'Database error: {e}')
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    username = input('შეიყვანეთ ახალი მომხმარებლის სახელი: ')
    password = input('შეიყვანეთ პაროლი: ')
    create_new_admin(username, password) 