"""
Expense Model
Handles expense-related database operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import get_db
from datetime import datetime, date


class Expense:
    """Expense model class"""
    
    def __init__(self, expense_id=None, user_id=None, category_id=None,
                 amount=None, description=None, expense_date=None,
                 payment_method='Cash', notes=None, category_name=None,
                 category_icon=None, category_color=None, created_at=None,
                 updated_at=None, **kwargs):
        self.expense_id = expense_id
        self.user_id = user_id
        self.category_id = category_id
        self.amount = amount
        self.description = description
        self.expense_date = expense_date
        self.payment_method = payment_method
        self.notes = notes
        self.category_name = category_name
        self.category_icon = category_icon
        self.category_color = category_color
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(user_id, category_id, amount, description, expense_date, 
               payment_method='Cash', notes=None):
        """Create a new expense"""
        db = get_db()
        
        query = """
            INSERT INTO expenses (user_id, category_id, amount, description, 
                                 expense_date, payment_method, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        expense_id = db.execute_query(
            query, 
            (user_id, category_id, amount, description, expense_date, payment_method, notes),
            fetch=False
        )
        
        if expense_id:
            return Expense(expense_id=expense_id, user_id=user_id, 
                          category_id=category_id, amount=amount,
                          description=description, expense_date=expense_date,
                          payment_method=payment_method, notes=notes)
        return None
    
    @staticmethod
    def get_by_id(expense_id, user_id=None):
        """Get expense by ID"""
        db = get_db()
        
        query = """
            SELECT e.*, c.category_name, c.icon as category_icon, c.color as category_color
            FROM expenses e
            JOIN categories c ON e.category_id = c.category_id
            WHERE e.expense_id = %s
        """
        params = [expense_id]
        
        if user_id:
            query += " AND e.user_id = %s"
            params.append(user_id)
        
        result = db.execute_query(query, tuple(params))
        
        if result and len(result) > 0:
            data = result[0]
            return Expense(**data)
        return None
    
    @staticmethod
    def get_user_expenses(user_id, start_date=None, end_date=None, 
                         category_id=None, limit=None, offset=0):
        """Get expenses for a user with optional filters"""
        db = get_db()
        
        query = """
            SELECT e.*, c.category_name, c.icon as category_icon, c.color as category_color
            FROM expenses e
            JOIN categories c ON e.category_id = c.category_id
            WHERE e.user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND e.expense_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND e.expense_date <= %s"
            params.append(end_date)
        
        if category_id:
            query += " AND e.category_id = %s"
            params.append(category_id)
        
        query += " ORDER BY e.expense_date DESC, e.created_at DESC"
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        result = db.execute_query(query, tuple(params))
        
        if result:
            return [Expense(**data) for data in result]
        return []
    
    @staticmethod
    def get_total_expenses(user_id, start_date=None, end_date=None, category_id=None):
        """Get total expenses for a user"""
        db = get_db()
        
        query = """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND expense_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND expense_date <= %s"
            params.append(end_date)
        
        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)
        
        result = db.execute_query(query, tuple(params))
        
        if result:
            return float(result[0]['total'])
        return 0.0
    
    @staticmethod
    def get_category_totals(user_id, start_date=None, end_date=None):
        """Get expense totals by category"""
        db = get_db()
        
        query = """
            SELECT c.category_id, c.category_name, c.icon, c.color,
                   COALESCE(SUM(e.amount), 0) as total,
                   COUNT(e.expense_id) as count
            FROM categories c
            LEFT JOIN expenses e ON c.category_id = e.category_id 
                AND e.user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND e.expense_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND e.expense_date <= %s"
            params.append(end_date)
        
        query += """
            GROUP BY c.category_id
            ORDER BY total DESC
        """
        
        result = db.execute_query(query, tuple(params))
        return result if result else []
    
    @staticmethod
    def get_monthly_totals(user_id, year):
        """Get monthly expense totals for a year"""
        db = get_db()
        
        query = """
            SELECT MONTH(expense_date) as month,
                   COALESCE(SUM(amount), 0) as total,
                   COUNT(*) as count
            FROM expenses
            WHERE user_id = %s AND YEAR(expense_date) = %s
            GROUP BY MONTH(expense_date)
            ORDER BY month
        """
        
        result = db.execute_query(query, (user_id, year))
        
        # Fill in missing months with 0
        monthly_data = {i: {'month': i, 'total': 0, 'count': 0} for i in range(1, 13)}
        if result:
            for row in result:
                monthly_data[row['month']] = row
        
        return list(monthly_data.values())
    
    @staticmethod
    def get_daily_totals(user_id, year, month):
        """Get daily expense totals for a month"""
        db = get_db()
        
        query = """
            SELECT DAY(expense_date) as day,
                   COALESCE(SUM(amount), 0) as total,
                   COUNT(*) as count
            FROM expenses
            WHERE user_id = %s 
              AND YEAR(expense_date) = %s 
              AND MONTH(expense_date) = %s
            GROUP BY DAY(expense_date)
            ORDER BY day
        """
        
        result = db.execute_query(query, (user_id, year, month))
        return result if result else []
    
    @staticmethod
    def get_expense_stats(user_id, start_date=None, end_date=None):
        """Get expense statistics"""
        db = get_db()
        
        query = """
            SELECT 
                COALESCE(SUM(amount), 0) as total,
                COALESCE(AVG(amount), 0) as average,
                COALESCE(MAX(amount), 0) as max_expense,
                COALESCE(MIN(amount), 0) as min_expense,
                COUNT(*) as count
            FROM expenses
            WHERE user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND expense_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND expense_date <= %s"
            params.append(end_date)
        
        result = db.execute_query(query, tuple(params))
        
        if result:
            return result[0]
        return {'total': 0, 'average': 0, 'max_expense': 0, 'min_expense': 0, 'count': 0}
    
    @staticmethod
    def get_recent_expenses(user_id, limit=5):
        """Get recent expenses"""
        return Expense.get_user_expenses(user_id, limit=limit)
    
    @staticmethod
    def search(user_id, search_term):
        """Search expenses by description"""
        db = get_db()
        
        query = """
            SELECT e.*, c.category_name, c.icon as category_icon, c.color as category_color
            FROM expenses e
            JOIN categories c ON e.category_id = c.category_id
            WHERE e.user_id = %s AND (e.description LIKE %s OR e.notes LIKE %s)
            ORDER BY e.expense_date DESC
        """
        
        search_pattern = f"%{search_term}%"
        result = db.execute_query(query, (user_id, search_pattern, search_pattern))
        
        if result:
            return [Expense(**data) for data in result]
        return []
    
    def update(self, category_id=None, amount=None, description=None,
               expense_date=None, payment_method=None, notes=None):
        """Update expense"""
        db = get_db()
        
        updates = []
        params = []
        
        if category_id is not None:
            updates.append("category_id = %s")
            params.append(category_id)
        
        if amount is not None:
            updates.append("amount = %s")
            params.append(amount)
        
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if expense_date is not None:
            updates.append("expense_date = %s")
            params.append(expense_date)
        
        if payment_method is not None:
            updates.append("payment_method = %s")
            params.append(payment_method)
        
        if notes is not None:
            updates.append("notes = %s")
            params.append(notes)
        
        if not updates:
            return False
        
        params.append(self.expense_id)
        
        query = f"""
            UPDATE expenses
            SET {', '.join(updates)}
            WHERE expense_id = %s
        """
        
        result = db.execute_query(query, tuple(params), fetch=False)
        return result is not None
    
    def delete(self):
        """Delete expense"""
        db = get_db()
        
        query = "DELETE FROM expenses WHERE expense_id = %s"
        result = db.execute_query(query, (self.expense_id,), fetch=False)
        return result is not None
    
    @staticmethod
    def delete_by_id(expense_id, user_id):
        """Delete expense by ID (with user verification)"""
        db = get_db()
        
        query = "DELETE FROM expenses WHERE expense_id = %s AND user_id = %s"
        result = db.execute_query(query, (expense_id, user_id), fetch=False)
        return result is not None
    
    def to_dict(self):
        """Convert expense to dictionary"""
        return {
            'expense_id': self.expense_id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category_name,
            'category_icon': self.category_icon,
            'category_color': self.category_color,
            'amount': float(self.amount) if self.amount else 0,
            'description': self.description,
            'expense_date': str(self.expense_date) if self.expense_date else None,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': str(self.created_at) if self.created_at else None
        }


class Category:
    """Category model class"""
    
    def __init__(self, category_id=None, category_name=None, icon=None,
                 color=None, description=None, is_default=False, name=None, **kwargs):
        self.category_id = category_id
        self.category_name = category_name or name
        self.name = category_name or name  # Alias
        self.icon = icon or '📦'
        self.color = color or '#667EEA'
        self.description = description
        self.is_default = is_default
    
    @staticmethod
    def get_all():
        """Get all categories"""
        db = get_db()
        
        query = """
            SELECT category_id, category_name, icon, color, description, is_default
            FROM categories
            ORDER BY is_default DESC, category_name ASC
        """
        
        result = db.execute_query(query)
        
        if result:
            return [Category(**data) for data in result]
        return []
    
    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        db = get_db()
        
        query = """
            SELECT category_id, category_name, icon, color, description, is_default
            FROM categories
            WHERE category_id = %s
        """
        
        result = db.execute_query(query, (category_id,))
        
        if result and len(result) > 0:
            return Category(**result[0])
        return None
    
    def to_dict(self):
        """Convert category to dictionary"""
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'icon': self.icon,
            'color': self.color,
            'description': self.description,
            'is_default': self.is_default
        }
