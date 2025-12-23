# Views package
from .login_view import LoginView
from .dashboard_view import DashboardView
from .expense_view import ExpenseListView, AddExpenseView
from .report_view import ReportView
from .budget_view import BudgetView
from .analytics_view import AnalyticsView


class ExpenseView:
    """Wrapper for expense views"""
    
    @staticmethod
    def create(parent, user, on_navigate, mode='list'):
        if mode == 'add':
            return AddExpenseView(parent, user, on_navigate)
        return ExpenseListView(parent, user, on_navigate)
