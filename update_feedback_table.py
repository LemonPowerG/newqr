import os
import psycopg2
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

def update_feedback_table():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Add new columns if they don't exist
        cur.execute('''
            ALTER TABLE feedback 
            ADD COLUMN IF NOT EXISTS service_rating INTEGER,
            ADD COLUMN IF NOT EXISTS cleanliness_rating INTEGER,
            ADD COLUMN IF NOT EXISTS staff_rating INTEGER,
            ADD COLUMN IF NOT EXISTS waiting_time_rating INTEGER,
            ADD COLUMN IF NOT EXISTS overall_rating INTEGER
        ''')
        
        # Update existing records
        cur.execute('''
            UPDATE feedback 
            SET 
                service_rating = rating,
                cleanliness_rating = rating,
                staff_rating = rating,
                waiting_time_rating = rating,
                overall_rating = rating
            WHERE service_rating IS NULL
        ''')
        
        # Drop old rating column
        cur.execute('ALTER TABLE feedback DROP COLUMN IF EXISTS rating')
        
        conn.commit()
        print('Feedback table successfully updated')
    except psycopg2.Error as e:
        print(f'Database error: {e}')
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    update_feedback_table() 