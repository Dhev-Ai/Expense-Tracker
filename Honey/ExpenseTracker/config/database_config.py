"""
Database Configuration
Update these settings according to your MySQL installation
"""

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',  # Enter your MySQL password here
    'database': 'expense_tracker',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True
}

# Connection pool settings
POOL_CONFIG = {
    'pool_name': 'expense_pool',
    'pool_size': 5,
    'pool_reset_session': True
}
