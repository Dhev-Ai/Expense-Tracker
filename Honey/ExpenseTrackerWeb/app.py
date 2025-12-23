"""
Expense Tracker - Flask Web Application
A responsive web app for tracking expenses
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import pooling
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'expense_tracker_secret_key_2025'

# Database Configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', os.environ.get('MYSQLHOST', 'localhost')),
    'user': os.environ.get('DB_USER', os.environ.get('MYSQLUSER', 'root')),
    'password': os.environ.get('DB_PASSWORD', os.environ.get('MYSQLPASSWORD', '12345')),
    'database': os.environ.get('DB_NAME', os.environ.get('MYSQLDATABASE', 'expense_tracker')),
    'port': int(os.environ.get('DB_PORT', os.environ.get('MYSQLPORT', 3306)))
}

# Connection Pool
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="expense_pool",
        pool_size=5,
        **DB_CONFIG
    )
    print("✅ Database connection pool created successfully!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    connection_pool = None

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, email, full_name):
        self.id = user_id
        self.username = username
        self.email = email
        self.full_name = full_name

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data:
            return User(user_data['user_id'], user_data['username'], 
                       user_data['email'], user_data['full_name'])
    return None

def get_db_connection():
    try:
        return connection_pool.get_connection()
    except:
        return None

# ==================== ROUTES ====================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", 
                          (username, username))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data and check_password_hash(user_data['password'], password):
                user = User(user_data['user_id'], user_data['username'],
                           user_data['email'], user_data['full_name'])
                login_user(user, remember=request.form.get('remember'))
                flash('Welcome back!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s",
                          (username, email))
            if cursor.fetchone():
                flash('Username or email already exists', 'error')
                cursor.close()
                conn.close()
                return render_template('register.html')
            
            # Create user
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (username, email, password, full_name)
                VALUES (%s, %s, %s, %s)
            """, (username, email, hashed_password, full_name))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    stats = {'total': 0, 'count': 0, 'avg': 0, 'max': 0}
    recent_expenses = []
    category_data = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get stats
        cursor.execute("""
            SELECT 
                COALESCE(SUM(amount), 0) as total,
                COUNT(*) as count,
                COALESCE(AVG(amount), 0) as avg,
                COALESCE(MAX(amount), 0) as max
            FROM expenses 
            WHERE user_id = %s AND MONTH(expense_date) = MONTH(CURRENT_DATE())
        """, (current_user.id,))
        stats = cursor.fetchone()
        
        # Get recent expenses
        cursor.execute("""
            SELECT e.*, c.category_name, c.icon
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.category_id
            WHERE e.user_id = %s
            ORDER BY e.expense_date DESC, e.created_at DESC
            LIMIT 5
        """, (current_user.id,))
        recent_expenses = cursor.fetchall()
        
        # Get category totals for pie chart
        cursor.execute("""
            SELECT c.category_name, c.icon, c.color, SUM(e.amount) as total
            FROM expenses e
            JOIN categories c ON e.category_id = c.category_id
            WHERE e.user_id = %s AND MONTH(e.expense_date) = MONTH(CURRENT_DATE())
            GROUP BY c.category_id
            ORDER BY total DESC
        """, (current_user.id,))
        category_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    return render_template('dashboard.html', stats=stats, 
                          recent_expenses=recent_expenses,
                          category_data=category_data)

@app.route('/expenses')
@login_required
def expenses():
    conn = get_db_connection()
    expenses_list = []
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get all expenses
        cursor.execute("""
            SELECT e.*, c.category_name, c.icon, c.color
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.category_id
            WHERE e.user_id = %s
            ORDER BY e.expense_date DESC, e.created_at DESC
        """, (current_user.id,))
        expenses_list = cursor.fetchall()
        
        # Get categories
        cursor.execute("SELECT * FROM categories ORDER BY category_name")
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    return render_template('expenses.html', expenses=expenses_list, categories=categories)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    conn = get_db_connection()
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories ORDER BY category_name")
        categories = cursor.fetchall()
        
        if request.method == 'POST':
            category_id = request.form.get('category_id')
            amount = request.form.get('amount')
            description = request.form.get('description')
            expense_date = request.form.get('expense_date')
            payment_method = request.form.get('payment_method', 'Cash')
            notes = request.form.get('notes', '')
            
            cursor.execute("""
                INSERT INTO expenses (user_id, category_id, amount, description, 
                                     expense_date, payment_method, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (current_user.id, category_id, amount, description,
                  expense_date, payment_method, notes))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Expense added successfully!', 'success')
            return redirect(url_for('expenses'))
        
        cursor.close()
        conn.close()
    
    return render_template('add_expense.html', categories=categories)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE expense_id = %s AND user_id = %s",
                      (expense_id, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Expense deleted!', 'success')
    return redirect(url_for('expenses'))

@app.route('/reports')
@login_required
def reports():
    period = request.args.get('period', 'month')
    conn = get_db_connection()
    
    category_data = []
    daily_data = []
    total = 0
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Date range based on period
        if period == 'week':
            start_date = datetime.now() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.now().replace(day=1)
        else:  # year
            start_date = datetime.now().replace(month=1, day=1)
        
        # Category totals
        cursor.execute("""
            SELECT c.category_name, c.icon, c.color, SUM(e.amount) as total
            FROM expenses e
            JOIN categories c ON e.category_id = c.category_id
            WHERE e.user_id = %s AND e.expense_date >= %s
            GROUP BY c.category_id
            ORDER BY total DESC
        """, (current_user.id, start_date.strftime('%Y-%m-%d')))
        category_data = cursor.fetchall()
        
        # Daily totals
        cursor.execute("""
            SELECT DATE(expense_date) as date, SUM(amount) as total
            FROM expenses
            WHERE user_id = %s AND expense_date >= %s
            GROUP BY DATE(expense_date)
            ORDER BY date
        """, (current_user.id, start_date.strftime('%Y-%m-%d')))
        daily_data = cursor.fetchall()
        
        total = sum(float(c['total']) for c in category_data) if category_data else 0
        
        cursor.close()
        conn.close()
    
    return render_template('reports.html', category_data=category_data,
                          daily_data=daily_data, total=total, period=period)

@app.route('/budget')
@login_required
def budget():
    conn = get_db_connection()
    budgets = []
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get budgets with spending
        cursor.execute("""
            SELECT b.*, c.category_name, c.icon, c.color,
                   COALESCE((SELECT SUM(e.amount) FROM expenses e 
                            WHERE e.category_id = b.category_id 
                            AND e.user_id = b.user_id
                            AND MONTH(e.expense_date) = b.month 
                            AND YEAR(e.expense_date) = b.year), 0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.category_id
            WHERE b.user_id = %s AND b.month = MONTH(CURRENT_DATE()) 
            AND b.year = YEAR(CURRENT_DATE())
        """, (current_user.id,))
        budgets = cursor.fetchall()
        
        cursor.execute("SELECT * FROM categories ORDER BY category_name")
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    return render_template('budget.html', budgets=budgets, categories=categories)

@app.route('/add_budget', methods=['POST'])
@login_required
def add_budget():
    category_id = request.form.get('category_id')
    amount = request.form.get('amount')
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        month = datetime.now().month
        year = datetime.now().year
        
        # Check if budget exists
        cursor.execute("""
            SELECT budget_id FROM budgets 
            WHERE user_id = %s AND category_id = %s AND month = %s AND year = %s
        """, (current_user.id, category_id, month, year))
        
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE budgets SET budget_amount = %s 
                WHERE budget_id = %s
            """, (amount, existing[0]))
        else:
            cursor.execute("""
                INSERT INTO budgets (user_id, category_id, budget_amount, month, year)
                VALUES (%s, %s, %s, %s, %s)
            """, (current_user.id, category_id, amount, month, year))
        
        conn.commit()
        cursor.close()
        conn.close()
        flash('Budget saved!', 'success')
    
    return redirect(url_for('budget'))

# API Endpoints for Charts
@app.route('/api/chart_data')
@login_required
def chart_data():
    conn = get_db_connection()
    data = {'labels': [], 'values': [], 'colors': []}
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.category_name, c.color, SUM(e.amount) as total
            FROM expenses e
            JOIN categories c ON e.category_id = c.category_id
            WHERE e.user_id = %s AND MONTH(e.expense_date) = MONTH(CURRENT_DATE())
            GROUP BY c.category_id
            ORDER BY total DESC
        """, (current_user.id,))
        
        for row in cursor.fetchall():
            # Clean category name (remove emoji)
            name = row['category_name']
            if name and len(name) > 2 and ord(name[0]) > 127:
                name = name.split(' ', 1)[-1] if ' ' in name else name
            data['labels'].append(name)
            data['values'].append(float(row['total']))
            data['colors'].append(row['color'])
        
        cursor.close()
        conn.close()
    
    return jsonify(data)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌐 EXPENSE TRACKER WEB APP")
    print("="*50)
    print("Open in browser: http://localhost:5000")
    print("Mobile access:   http://172.17.57.69:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
