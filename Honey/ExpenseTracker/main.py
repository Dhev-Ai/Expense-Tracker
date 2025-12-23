"""
Expense Tracker - Main Application
Enhanced version with interactive UI, charts, and budget tracking
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.styles import COLORS, FONTS, DIMENSIONS, MENU_ITEMS
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.expense_view import ExpenseListView, AddExpenseView
from views.report_view import ReportView
from views.budget_view import BudgetView
from views.analytics_view import AnalyticsView


class ExpenseTrackerApp:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💰 Expense Tracker Pro")
        self.root.geometry("1280x800")
        self.root.minsize(1100, 700)
        self.root.configure(bg=COLORS['bg_primary'])
        
        # Center window
        self.center_window()
        
        # Set icon if available
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Current user
        self.current_user = None
        self.current_view = None
        self.current_view_name = 'dashboard'
        
        # Create styles
        self.create_styles()
        
        # Show login
        self.show_login()
        
        # Start app
        self.root.mainloop()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = 1280
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_styles(self):
        """Create ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Scrollbar
        style.configure(
            "Custom.Vertical.TScrollbar",
            background=COLORS['bg_tertiary'],
            troughcolor=COLORS['bg_secondary'],
            borderwidth=0,
            arrowsize=0
        )
        
        # Entry
        style.configure(
            "Custom.TEntry",
            fieldbackground=COLORS['input_bg'],
            background=COLORS['input_bg'],
            foreground=COLORS['text_primary'],
            borderwidth=0,
            padding=10
        )
        
        # Combobox
        style.configure(
            "Custom.TCombobox",
            fieldbackground=COLORS['input_bg'],
            background=COLORS['input_bg'],
            foreground=COLORS['text_primary'],
            borderwidth=0,
            padding=8
        )
    
    def show_login(self):
        """Show login view"""
        # Clear root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show login
        login_view = LoginView(self.root, self.on_login_success)
        login_view.pack(fill=tk.BOTH, expand=True)
    
    def on_login_success(self, user):
        """Handle successful login"""
        self.current_user = user
        self.show_main_app()
    
    def show_main_app(self):
        """Show main application with sidebar"""
        # Clear root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar = self.create_sidebar(main_container)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Content area
        self.content_frame = tk.Frame(main_container, bg=COLORS['bg_secondary'])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Show dashboard by default
        self.navigate_to('dashboard')
    
    def create_sidebar(self, parent):
        """Create sidebar navigation"""
        sidebar = tk.Frame(
            parent,
            bg=COLORS['sidebar_bg'],
            width=DIMENSIONS['sidebar_width']
        )
        sidebar.pack_propagate(False)
        
        # Logo/Brand section
        brand = tk.Frame(sidebar, bg=COLORS['sidebar_bg'])
        brand.pack(fill=tk.X, padx=20, pady=25)
        
        # Logo icon
        logo_frame = tk.Frame(brand, bg=COLORS['primary'], width=50, height=50)
        logo_frame.pack(side=tk.LEFT)
        logo_frame.pack_propagate(False)
        
        tk.Label(
            logo_frame,
            text="💰",
            font=('Segoe UI', 20),
            bg=COLORS['primary'],
            fg=COLORS['text_white']
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # App name
        brand_text = tk.Frame(brand, bg=COLORS['sidebar_bg'])
        brand_text.pack(side=tk.LEFT, padx=(12, 0))
        
        tk.Label(
            brand_text,
            text="Expense",
            font=FONTS['heading_small'],
            bg=COLORS['sidebar_bg'],
            fg=COLORS['text_white']
        ).pack(anchor='w')
        
        tk.Label(
            brand_text,
            text="Tracker Pro",
            font=FONTS['body'],
            bg=COLORS['sidebar_bg'],
            fg=COLORS['text_light']
        ).pack(anchor='w')
        
        # Divider
        tk.Frame(sidebar, bg=COLORS['border'], height=1).pack(fill=tk.X, padx=20, pady=10)
        
        # Navigation menu
        nav_frame = tk.Frame(sidebar, bg=COLORS['sidebar_bg'])
        nav_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.nav_buttons = {}
        
        for item in MENU_ITEMS:
            self.create_nav_item(nav_frame, item)
        
        # Spacer
        tk.Frame(sidebar, bg=COLORS['sidebar_bg']).pack(fill=tk.BOTH, expand=True)
        
        # User profile section
        profile = tk.Frame(sidebar, bg=COLORS['sidebar_bg'])
        profile.pack(fill=tk.X, padx=15, pady=20)
        
        # User card
        user_card = tk.Frame(profile, bg=COLORS['sidebar_hover'])
        user_card.pack(fill=tk.X)
        
        user_inner = tk.Frame(user_card, bg=COLORS['sidebar_hover'])
        user_inner.pack(fill=tk.X, padx=12, pady=12)
        
        # Avatar
        avatar = tk.Frame(user_inner, bg=COLORS['primary'], width=40, height=40)
        avatar.pack(side=tk.LEFT)
        avatar.pack_propagate(False)
        
        initials = self.current_user.full_name[:2].upper() if self.current_user else "U"
        tk.Label(
            avatar,
            text=initials,
            font=FONTS['body_medium'],
            bg=COLORS['primary'],
            fg=COLORS['text_white']
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # User info
        user_info = tk.Frame(user_inner, bg=COLORS['sidebar_hover'])
        user_info.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        tk.Label(
            user_info,
            text=self.current_user.full_name if self.current_user else "User",
            font=FONTS['body_medium'],
            bg=COLORS['sidebar_hover'],
            fg=COLORS['text_white']
        ).pack(anchor='w')
        
        tk.Label(
            user_info,
            text=self.current_user.email if self.current_user else "",
            font=FONTS['caption'],
            bg=COLORS['sidebar_hover'],
            fg=COLORS['text_light']
        ).pack(anchor='w')
        
        # Logout button
        logout_btn = tk.Button(
            profile,
            text="🚪 Logout",
            font=FONTS['body'],
            bg=COLORS['sidebar_bg'],
            fg=COLORS['text_light'],
            activebackground=COLORS['sidebar_hover'],
            activeforeground=COLORS['text_white'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self.logout
        )
        logout_btn.pack(fill=tk.X, pady=(10, 0))
        logout_btn.bind('<Enter>', lambda e: logout_btn.config(bg=COLORS['error'], fg=COLORS['text_white']))
        logout_btn.bind('<Leave>', lambda e: logout_btn.config(bg=COLORS['sidebar_bg'], fg=COLORS['text_light']))
        
        return sidebar
    
    def create_nav_item(self, parent, item):
        """Create navigation menu item"""
        btn = tk.Button(
            parent,
            text=f"  {item['icon']}  {item['label']}",
            font=FONTS['body_medium'],
            bg=COLORS['sidebar_bg'],
            fg=COLORS['text_light'],
            activebackground=COLORS['sidebar_active'],
            activeforeground=COLORS['text_white'],
            relief=tk.FLAT,
            anchor='w',
            cursor='hand2',
            padx=15,
            pady=12,
            command=lambda k=item['key']: self.navigate_to(k)
        )
        btn.pack(fill=tk.X, pady=2)
        
        # Hover effects
        def on_enter(e, button=btn, key=item['key']):
            if self.current_view_name != key:
                button.config(bg=COLORS['sidebar_hover'])
        
        def on_leave(e, button=btn, key=item['key']):
            if self.current_view_name != key:
                button.config(bg=COLORS['sidebar_bg'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        self.nav_buttons[item['key']] = btn
    
    def update_nav_selection(self, key):
        """Update navigation button selection"""
        for nav_key, btn in self.nav_buttons.items():
            if nav_key == key:
                btn.config(
                    bg=COLORS['sidebar_active'],
                    fg=COLORS['text_white']
                )
            else:
                btn.config(
                    bg=COLORS['sidebar_bg'],
                    fg=COLORS['text_light']
                )
    
    def navigate_to(self, view_name):
        """Navigate to a view"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.current_view_name = view_name
        self.update_nav_selection(view_name)
        
        # Create new view
        if view_name == 'dashboard':
            self.current_view = DashboardView(
                self.content_frame,
                self.current_user,
                self.navigate_to
            )
        elif view_name == 'expenses':
            self.current_view = ExpenseListView(
                self.content_frame,
                self.current_user,
                self.navigate_to
            )
        elif view_name == 'add_expense':
            self.current_view = AddExpenseView(
                self.content_frame,
                self.current_user,
                self.navigate_to
            )
        elif view_name == 'reports':
            self.current_view = ReportView(
                self.content_frame,
                self.current_user,
                self.navigate_to
            )
        elif view_name == 'budget':
            self.current_view = BudgetView(
                self.content_frame,
                self.current_user,
                self.navigate_to
            )
        elif view_name == 'analytics':
            self.current_view = AnalyticsView(
                self.content_frame,
                self.current_user,
                self.navigate_to
            )
        else:
            # Default to dashboard
            self.current_view = DashboardView(
                self.content_frame,
                self.current_user,
                self.navigate_to
            )
        
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    def logout(self):
        """Logout current user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.show_login()


def main():
    """Main entry point"""
    try:
        app = ExpenseTrackerApp()
    except Exception as e:
        import traceback
        print(f"Error starting application: {e}")
        traceback.print_exc()
        
        # Show error dialog
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Error",
            f"Failed to start application:\n{str(e)}\n\nCheck database connection."
        )
        root.destroy()


if __name__ == "__main__":
    main()
