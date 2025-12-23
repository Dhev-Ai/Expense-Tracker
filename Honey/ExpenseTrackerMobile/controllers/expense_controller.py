"""
Expense Controller
Handles expense-related operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.expense import Expense, Category
from datetime import datetime, date
from utils.helpers import format_currency, export_to_csv, generate_report_filename


class ExpenseController:
    """Expense controller class"""
    
    @staticmethod
    def add_expense(user_id, category_id, amount, description, 
                   expense_date, payment_method='Cash', notes=None):
        """
        Add new expense
        Returns: (success, message, expense)
        """
        # Validate inputs
        if not all([user_id, category_id, amount, description, expense_date]):
            return False, "Please fill all required fields", None
        
        try:
            amount = float(amount)
            if amount <= 0:
                return False, "Amount must be greater than 0", None
        except ValueError:
            return False, "Invalid amount", None
        
        # Create expense
        expense = Expense.create(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            description=description,
            expense_date=expense_date,
            payment_method=payment_method,
            notes=notes
        )
        
        if expense:
            return True, "Expense added successfully!", expense
        else:
            return False, "Failed to add expense", None
    
    @staticmethod
    def update_expense(expense_id, user_id, **kwargs):
        """
        Update expense
        Returns: (success, message)
        """
        expense = Expense.get_by_id(expense_id, user_id)
        
        if not expense:
            return False, "Expense not found"
        
        if 'amount' in kwargs:
            try:
                kwargs['amount'] = float(kwargs['amount'])
                if kwargs['amount'] <= 0:
                    return False, "Amount must be greater than 0"
            except ValueError:
                return False, "Invalid amount"
        
        success = expense.update(**kwargs)
        
        if success:
            return True, "Expense updated successfully!"
        else:
            return False, "Failed to update expense"
    
    @staticmethod
    def delete_expense(expense_id, user_id):
        """
        Delete expense
        Returns: (success, message)
        """
        success = Expense.delete_by_id(expense_id, user_id)
        
        if success:
            return True, "Expense deleted successfully!"
        else:
            return False, "Failed to delete expense"
    
    @staticmethod
    def get_expenses(user_id, start_date=None, end_date=None, 
                    category_id=None, limit=None, offset=0):
        """Get user expenses with filters"""
        return Expense.get_user_expenses(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            limit=limit,
            offset=offset
        )
    
    @staticmethod
    def get_expense_by_id(expense_id, user_id):
        """Get single expense"""
        return Expense.get_by_id(expense_id, user_id)
    
    @staticmethod
    def search_expenses(user_id, search_term):
        """Search expenses"""
        return Expense.search(user_id, search_term)
    
    @staticmethod
    def get_dashboard_data(user_id):
        """Get dashboard summary data"""
        today = datetime.now()
        
        # Current month date range
        month_start = today.replace(day=1).date()
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1).date()
        else:
            month_end = today.replace(month=today.month + 1, day=1).date()
        
        # Today's date
        today_date = today.date()
        
        # Get statistics
        monthly_stats = Expense.get_expense_stats(user_id, month_start, month_end)
        today_total = Expense.get_total_expenses(user_id, today_date, today_date)
        yearly_total = Expense.get_total_expenses(
            user_id, 
            today.replace(month=1, day=1).date(),
            today.replace(month=12, day=31).date()
        )
        
        # Get category breakdown for current month
        category_totals = Expense.get_category_totals(user_id, month_start, month_end)
        
        # Get recent expenses
        recent_expenses = Expense.get_recent_expenses(user_id, limit=5)
        
        # Get monthly trend for the year
        monthly_trend = Expense.get_monthly_totals(user_id, today.year)
        
        return {
            'monthly_total': float(monthly_stats['total']),
            'monthly_average': float(monthly_stats['average']),
            'monthly_count': monthly_stats['count'],
            'today_total': float(today_total),
            'yearly_total': float(yearly_total),
            'category_totals': category_totals,
            'recent_expenses': recent_expenses,
            'monthly_trend': monthly_trend,
            'current_month': today.strftime('%B %Y')
        }
    
    @staticmethod
    def get_report_data(user_id, start_date=None, end_date=None):
        """Get report data for charts and analysis"""
        today = datetime.now()
        
        # Default to current month if no dates provided
        if not start_date:
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
        if not end_date:
            end_date = today.strftime('%Y-%m-%d')
        
        # Convert strings to date if needed
        if isinstance(start_date, str):
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_dt = start_date
        
        if isinstance(end_date, str):
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_dt = end_date
        
        # Get category totals
        category_totals = Expense.get_category_totals(user_id, start_date, end_date)
        
        # Get expenses
        expenses = Expense.get_user_expenses(user_id, start_date, end_date)
        
        # Get daily totals
        daily_trend = Expense.get_daily_totals(user_id, start_dt.year, start_dt.month)
        
        # Get monthly totals
        monthly_trend = Expense.get_monthly_totals(user_id, today.year)
        
        return {
            'category_totals': category_totals,
            'expenses': expenses,
            'daily_trend': daily_trend,
            'monthly_trend': monthly_trend,
            'start_date': start_date,
            'end_date': end_date
        }
    
    @staticmethod
    def export_expenses(user_id, expenses, filepath=None):
        """Export expenses to CSV"""
        if not filepath:
            filepath = generate_report_filename('expenses')
        
        headers = ['Date', 'Category', 'Description', 'Amount', 'Payment Method', 'Notes']
        
        data = []
        for exp in expenses:
            data.append([
                str(exp.expense_date),
                exp.category_name or '',
                exp.description or '',
                float(exp.amount) if exp.amount else 0,
                exp.payment_method or '',
                exp.notes or ''
            ])
        
        success, result = export_to_csv(data, filepath, headers)
        
        if success:
            return True, f"Exported to {result}"
        else:
            return False, f"Export failed: {result}"
    
    @staticmethod
    def get_categories():
        """Get all expense categories"""
        return Category.get_all()
    
    @staticmethod
    def get_category_by_id(category_id):
        """Get category by ID"""
        return Category.get_by_id(category_id)
    
    @staticmethod
    def set_category_budget(user_id, category_id, amount):
        """Set budget for a category"""
        from database.db_connection import DatabaseConnection
        
        db = DatabaseConnection()
        conn = db.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Check if budget exists
            cursor.execute(
                "SELECT id FROM budgets WHERE user_id = %s AND category_id = %s",
                (user_id, category_id)
            )
            existing = cursor.fetchone()
            
            current_month = datetime.now().strftime('%Y-%m-01')
            
            if existing:
                cursor.execute(
                    """UPDATE budgets 
                       SET amount = %s, month = %s 
                       WHERE user_id = %s AND category_id = %s""",
                    (amount, current_month, user_id, category_id)
                )
            else:
                cursor.execute(
                    """INSERT INTO budgets (user_id, category_id, amount, month)
                       VALUES (%s, %s, %s, %s)""",
                    (user_id, category_id, amount, current_month)
                )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting budget: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_category_budget(user_id, category_id):
        """Get budget for a category"""
        from database.db_connection import DatabaseConnection
        
        db = DatabaseConnection()
        conn = db.get_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT amount FROM budgets 
                   WHERE user_id = %s AND category_id = %s
                   ORDER BY month DESC LIMIT 1""",
                (user_id, category_id)
            )
            result = cursor.fetchone()
            return float(result[0]) if result else 0
        except Exception as e:
            print(f"Error getting budget: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()
