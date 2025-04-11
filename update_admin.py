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

def update_admin_password(username, new_password):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Hash new password
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Update password
        cur.execute('UPDATE users SET password = %s WHERE username = %s',
                   (password_hash, username))
        conn.commit()
        print(f'პაროლი წარმატებით განახლდა მომხმარებლისთვის: {username}')
    except psycopg2.Error as e:
        print(f'Database error: {e}')
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    username = input('შეიყვანეთ მომხმარებლის სახელი: ')
    new_password = input('შეიყვანეთ ახალი პაროლი: ')
    update_admin_password(username, new_password) 