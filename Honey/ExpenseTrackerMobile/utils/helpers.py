"""
Utility Helper Functions
Common functions used throughout the application
"""

import hashlib
import re
from datetime import datetime, date
from decimal import Decimal
import csv
import os


def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """Validate username (alphanumeric, 3-20 chars)"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None


def validate_password(password):
    """
    Validate password strength
    - At least 6 characters
    - Contains at least one letter and one number
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"


def format_currency(amount, symbol='₹'):
    """Format amount as currency"""
    if isinstance(amount, (int, float, Decimal)):
        return f"{symbol}{amount:,.2f}"
    return f"{symbol}0.00"


def format_date(date_obj, format_str='%d %b %Y'):
    """Format date object to string"""
    if isinstance(date_obj, (datetime, date)):
        return date_obj.strftime(format_str)
    return str(date_obj)


def parse_date(date_str, format_str='%Y-%m-%d'):
    """Parse string to date object"""
    try:
        return datetime.strptime(date_str, format_str).date()
    except ValueError:
        return None


def get_current_month_year():
    """Get current month and year"""
    today = datetime.now()
    return today.month, today.year


def get_month_name(month_num):
    """Get month name from number"""
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    if 1 <= month_num <= 12:
        return months[month_num - 1]
    return ''


def get_month_short_name(month_num):
    """Get short month name from number"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if 1 <= month_num <= 12:
        return months[month_num - 1]
    return ''


def get_date_range(period='month'):
    """Get start and end date for a period"""
    today = datetime.now()
    
    if period == 'today':
        return today.date(), today.date()
    elif period == 'week':
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start.date(), end.date()
    elif period == 'month':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end = today.replace(month=today.month + 1, day=1)
        end = end - timedelta(days=1)
        return start.date(), end.date()
    elif period == 'year':
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return start.date(), end.date()
    
    return today.date(), today.date()


from datetime import timedelta


def calculate_percentage(part, whole):
    """Calculate percentage"""
    if whole == 0:
        return 0
    return round((part / whole) * 100, 1)


def truncate_text(text, max_length=50):
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def export_to_csv(data, filename, headers=None):
    """Export data to CSV file"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if headers:
                writer.writerow(headers)
            for row in data:
                if isinstance(row, dict):
                    writer.writerow(row.values())
                else:
                    writer.writerow(row)
        return True, filename
    except Exception as e:
        return False, str(e)


def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


def get_greeting():
    """Get time-based greeting"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"


def generate_report_filename(report_type, extension='csv'):
    """Generate filename for reports"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{report_type}_{timestamp}.{extension}"


# Payment method options
PAYMENT_METHODS = [
    'Cash',
    'Credit Card',
    'Debit Card',
    'UPI',
    'Net Banking',
    'Other'
]


# Time period options for filtering
TIME_PERIODS = [
    ('Today', 'today'),
    ('This Week', 'week'),
    ('This Month', 'month'),
    ('This Year', 'year'),
    ('All Time', 'all'),
]
