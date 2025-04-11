from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import qrcode
import os
from datetime import datetime
import psycopg2
from functools import wraps
import hashlib
from urllib.parse import urlparse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes session lifetime

# Database connection configuration
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

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('გთხოვთ გაიაროთ ავტორიზაცია', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('გთხოვთ გაიაროთ ავტორიზაცია', 'error')
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash('არ გაქვთ წვდომა ამ გვერდზე', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize database tables
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create branches table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS branches (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(255) NOT NULL
            )
        ''')
        
        # Create feedback table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                branch_id INTEGER REFERENCES branches(id),
                service_rating INTEGER NOT NULL,
                cleanliness_rating INTEGER NOT NULL,
                staff_rating INTEGER NOT NULL,
                waiting_time_rating INTEGER NOT NULL,
                overall_rating INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    except psycopg2.Error as e:
        print(f'Database error: {e}')
    finally:
        cur.close()
        conn.close()

# Initialize database on startup
init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feedback/<int:branch_id>', methods=['GET', 'POST'])
def feedback(branch_id):
    if request.method == 'POST':
        service_rating = request.form.get('service_rating')
        cleanliness_rating = request.form.get('cleanliness_rating')
        staff_rating = request.form.get('staff_rating')
        waiting_time_rating = request.form.get('waiting_time_rating')
        overall_rating = request.form.get('overall_rating')
        comment = request.form.get('comment')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO feedback (branch_id, service_rating, cleanliness_rating, staff_rating, waiting_time_rating, overall_rating, comment) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (branch_id, service_rating, cleanliness_rating, staff_rating, waiting_time_rating, overall_rating, comment)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('thank_you'))

    return render_template('feedback.html', branch_id=branch_id)

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/admin')
@admin_required
def admin():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all branches
    cur.execute('SELECT * FROM branches ORDER BY id DESC')
    branches = cur.fetchall()
    
    # Get statistics for each branch
    for branch in branches:
        cur.execute('''
            SELECT 
                COUNT(*) as total_feedback,
                AVG(service_rating) as avg_service,
                AVG(cleanliness_rating) as avg_cleanliness,
                AVG(staff_rating) as avg_staff,
                AVG(waiting_time_rating) as avg_waiting,
                AVG(overall_rating) as avg_overall
            FROM feedback 
            WHERE branch_id = %s
        ''', (branch[0],))  # id is at index 0
        stats = cur.fetchone()
        branch['stats'] = stats
    
    cur.close()
    conn.close()
    
    return render_template('admin/dashboard.html', branches=branches)

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and hashlib.sha256(password.encode()).hexdigest() == user[2]:  # password is at index 2
            session['user_id'] = user[0]  # id is at index 0
            session['is_admin'] = user[3]  # is_admin is at index 3
            return redirect(url_for('admin'))
        else:
            flash('არასწორი მომხმარებელი ან პაროლი', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/branch/add', methods=['GET', 'POST'])
@admin_required
def add_branch():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO branches (name, location) VALUES (%s, %s) RETURNING id', (name, location))
        branch_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"{request.host_url}feedback/{branch_id}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        qr_code_path = os.path.join('static', 'qr_codes', f'{branch_id}.png')
        os.makedirs(os.path.dirname(qr_code_path), exist_ok=True)
        img.save(qr_code_path)
        
        flash('ფილიალი წარმატებით დაემატა', 'success')
        return redirect(url_for('admin'))
    
    return render_template('admin/add_branch.html')

@app.route('/admin/branch/delete/<int:branch_id>', methods=['POST'])
@admin_required
def delete_branch(branch_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Delete branch
    cur.execute('DELETE FROM branches WHERE id = %s', (branch_id,))
    conn.commit()
    
    # Delete associated feedback
    cur.execute('DELETE FROM feedback WHERE branch_id = %s', (branch_id,))
    conn.commit()
    
    cur.close()
    conn.close()
    
    # Delete QR code file
    qr_code_path = os.path.join('static', 'qr_codes', f'{branch_id}.png')
    if os.path.exists(qr_code_path):
        os.remove(qr_code_path)
    
    flash('ფილიალი წარმატებით წაიშალა', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/feedback/<int:branch_id>')
@admin_required
def view_feedback(branch_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get branch name
    cur.execute('SELECT name FROM branches WHERE id = %s', (branch_id,))
    branch = cur.fetchone()
    
    # Get feedback data
    cur.execute('''
        SELECT 
            service_rating,
            cleanliness_rating,
            staff_rating,
            waiting_time_rating,
            overall_rating,
            comment,
            created_at
        FROM feedback 
        WHERE branch_id = %s 
        ORDER BY created_at DESC
    ''', (branch_id,))
    feedback_data = cur.fetchall()
    
    # Calculate statistics
    cur.execute('''
        SELECT 
            AVG(service_rating) as avg_service,
            AVG(cleanliness_rating) as avg_cleanliness,
            AVG(staff_rating) as avg_staff,
            AVG(waiting_time_rating) as avg_waiting,
            AVG(overall_rating) as avg_overall,
            COUNT(*) as total_feedback
        FROM feedback 
        WHERE branch_id = %s
    ''', (branch_id,))
    stats = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return render_template('view_feedback.html', 
                         branch=branch,
                         feedback_data=feedback_data,
                         stats=stats)

@app.route('/admin/create', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('პაროლები არ ემთხვევა ერთმანეთს', 'error')
            return render_template('admin/create_admin.html')
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute('INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)',
                       (username, password_hash, True))
            conn.commit()
            flash('ადმინისტრატორი წარმატებით შეიქმნა', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('მომხმარებელი ამ სახელით უკვე არსებობს', 'error')
        finally:
            cur.close()
            conn.close()
    
    return render_template('admin/create_admin.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 