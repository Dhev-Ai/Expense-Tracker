"""
Expense Tracker - Kivy Mobile Application
Cross-platform mobile app for tracking expenses
Can be compiled to Android APK using Buildozer
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore

import mysql.connector
from datetime import datetime, timedelta
from functools import partial
import hashlib
import os

# Set window size for development (will be fullscreen on mobile)
Window.size = (400, 700)

# Colors
COLORS = {
    'primary': '#667EEA',
    'primary_dark': '#5A67D8',
    'secondary': '#48BB78',
    'danger': '#F56565',
    'warning': '#ED8936',
    'bg_dark': '#1A202C',
    'bg_card': '#2D3748',
    'text_primary': '#F7FAFC',
    'text_secondary': '#A0AEC0',
    'border': '#4A5568'
}

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'expense_tracker'
}


def get_db_connection():
    """Get database connection"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database error: {e}")
        return None


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


class RoundedButton(Button):
    """Custom rounded button"""
    def __init__(self, bg_color='#667EEA', **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.bg_color = get_color_from_hex(bg_color)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])


class StyledTextInput(TextInput):
    """Custom styled text input"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#2D3748')
        self.foreground_color = get_color_from_hex('#F7FAFC')
        self.cursor_color = get_color_from_hex('#667EEA')
        self.hint_text_color = get_color_from_hex('#718096')
        self.padding = [dp(15), dp(12)]
        self.font_size = sp(16)
        self.multiline = False


class ExpenseCard(BoxLayout):
    """Expense item card"""
    def __init__(self, expense_data, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = [dp(15), dp(10)]
        self.spacing = dp(10)
        
        # Background
        with self.canvas.before:
            Color(*get_color_from_hex('#2D3748'))
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Icon
        icon_label = Label(
            text=expense_data.get('icon', '📦'),
            font_size=sp(24),
            size_hint_x=None,
            width=dp(40)
        )
        self.add_widget(icon_label)
        
        # Info
        info_box = BoxLayout(orientation='vertical', spacing=dp(2))
        info_box.add_widget(Label(
            text=expense_data.get('description', 'No description'),
            font_size=sp(14),
            color=get_color_from_hex('#F7FAFC'),
            halign='left',
            text_size=(dp(150), None)
        ))
        info_box.add_widget(Label(
            text=f"{expense_data.get('category', '')} • {expense_data.get('date', '')}",
            font_size=sp(11),
            color=get_color_from_hex('#A0AEC0'),
            halign='left',
            text_size=(dp(150), None)
        ))
        self.add_widget(info_box)
        
        # Amount
        amount_label = Label(
            text=f"-₹{expense_data.get('amount', 0):.0f}",
            font_size=sp(16),
            bold=True,
            color=get_color_from_hex('#F56565'),
            size_hint_x=None,
            width=dp(80)
        )
        self.add_widget(amount_label)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class StatCard(BoxLayout):
    """Statistics card widget"""
    def __init__(self, title, value, icon, color='#667EEA', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [dp(15), dp(12)]
        self.spacing = dp(5)
        
        # Background with gradient effect
        with self.canvas.before:
            Color(*get_color_from_hex(color))
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Icon and title
        header = BoxLayout(size_hint_y=None, height=dp(25))
        header.add_widget(Label(
            text=f"{icon} {title}",
            font_size=sp(12),
            color=(1, 1, 1, 0.9),
            halign='left'
        ))
        self.add_widget(header)
        
        # Value
        self.add_widget(Label(
            text=value,
            font_size=sp(22),
            bold=True,
            color=(1, 1, 1, 1),
            halign='left'
        ))
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class LoginScreen(Screen):
    """Login screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('user_data.json')
        self.build_ui()
        
        # Auto-login if saved
        Clock.schedule_once(self.check_saved_login, 0.5)
    
    def build_ui(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        # Background
        with main_layout.canvas.before:
            Color(*get_color_from_hex('#1A202C'))
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Spacer
        main_layout.add_widget(BoxLayout(size_hint_y=0.1))
        
        # Logo
        logo_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        logo_box.add_widget(Label(
            text='💰',
            font_size=sp(80)
        ))
        logo_box.add_widget(Label(
            text='Expense Tracker',
            font_size=sp(28),
            bold=True,
            color=get_color_from_hex('#667EEA')
        ))
        logo_box.add_widget(Label(
            text='GPS',
            font_size=sp(12),
            color=get_color_from_hex('#A0AEC0')
        ))
        main_layout.add_widget(logo_box)
        
        # Spacer
        main_layout.add_widget(BoxLayout(size_hint_y=0.05))
        
        # Form
        form = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, height=dp(200))
        
        self.username_input = StyledTextInput(
            hint_text='Username or Email',
            size_hint_y=None,
            height=dp(50)
        )
        form.add_widget(self.username_input)
        
        self.password_input = StyledTextInput(
            hint_text='Password',
            password=True,
            size_hint_y=None,
            height=dp(50)
        )
        form.add_widget(self.password_input)
        
        # Remember me
        remember_box = BoxLayout(size_hint_y=None, height=dp(30))
        self.remember_btn = Button(
            text='☐ Remember me',
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex('#A0AEC0'),
            font_size=sp(14),
            halign='left'
        )
        self.remember_btn.bind(on_press=self.toggle_remember)
        self.remember_checked = False
        remember_box.add_widget(self.remember_btn)
        form.add_widget(remember_box)
        
        main_layout.add_widget(form)
        
        # Login button
        login_btn = RoundedButton(
            text='🚀  Sign In',
            font_size=sp(18),
            size_hint_y=None,
            height=dp(55),
            bg_color='#667EEA'
        )
        login_btn.bind(on_press=self.login)
        main_layout.add_widget(login_btn)
        
        # Register link
        register_box = BoxLayout(size_hint_y=None, height=dp(40))
        register_box.add_widget(Label(
            text="Don't have an account?",
            font_size=sp(14),
            color=get_color_from_hex('#A0AEC0')
        ))
        register_btn = Button(
            text='Sign Up',
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex('#667EEA'),
            font_size=sp(14),
            bold=True
        )
        register_btn.bind(on_press=self.go_to_register)
        register_box.add_widget(register_btn)
        main_layout.add_widget(register_box)
        
        # Spacer
        main_layout.add_widget(BoxLayout())
        
        self.add_widget(main_layout)
        self.main_layout = main_layout
    
    def update_bg(self, *args):
        self.bg.pos = self.main_layout.pos
        self.bg.size = self.main_layout.size
    
    def toggle_remember(self, instance):
        self.remember_checked = not self.remember_checked
        instance.text = '☑ Remember me' if self.remember_checked else '☐ Remember me'
    
    def check_saved_login(self, dt):
        if self.store.exists('user'):
            user = self.store.get('user')
            self.username_input.text = user.get('username', '')
            self.password_input.text = user.get('password', '')
            self.remember_checked = True
            self.remember_btn.text = '☑ Remember me'
    
    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_popup('Error', 'Please enter username and password')
            return
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username = %s OR email = %s",
                (username, username)
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                # Check password (hashed)
                stored_pass = user['password']
                # Try both hashed and plain comparison for compatibility
                if stored_pass == hash_password(password) or \
                   stored_pass == password or \
                   self.check_werkzeug_hash(stored_pass, password):
                    
                    # Save login if remember is checked
                    if self.remember_checked:
                        self.store.put('user', username=username, password=password)
                    elif self.store.exists('user'):
                        self.store.delete('user')
                    
                    # Go to dashboard
                    app = App.get_running_app()
                    app.current_user = user
                    self.manager.current = 'dashboard'
                    return
            
            self.show_popup('Error', 'Invalid username or password')
        else:
            self.show_popup('Error', 'Could not connect to database')
    
    def check_werkzeug_hash(self, stored, password):
        """Check werkzeug password hash format"""
        try:
            from werkzeug.security import check_password_hash
            return check_password_hash(stored, password)
        except:
            return False
    
    def go_to_register(self, instance):
        self.manager.current = 'register'
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, font_size=sp(14)),
            size_hint=(0.8, 0.3),
            background_color=get_color_from_hex('#2D3748')
        )
        popup.open()


class RegisterScreen(Screen):
    """Registration screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
        
        with main_layout.canvas.before:
            Color(*get_color_from_hex('#1A202C'))
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(60))
        back_btn = Button(
            text='←',
            font_size=sp(24),
            size_hint_x=None,
            width=dp(50),
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex('#F7FAFC')
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        header.add_widget(back_btn)
        header.add_widget(Label(
            text='Create Account',
            font_size=sp(22),
            bold=True,
            color=get_color_from_hex('#F7FAFC')
        ))
        header.add_widget(BoxLayout(size_hint_x=None, width=dp(50)))
        main_layout.add_widget(header)
        
        # Icon
        main_layout.add_widget(Label(
            text='🎯',
            font_size=sp(60),
            size_hint_y=None,
            height=dp(80)
        ))
        
        # Form
        self.fullname_input = StyledTextInput(hint_text='Full Name', size_hint_y=None, height=dp(50))
        main_layout.add_widget(self.fullname_input)
        
        self.username_input = StyledTextInput(hint_text='Username', size_hint_y=None, height=dp(50))
        main_layout.add_widget(self.username_input)
        
        self.email_input = StyledTextInput(hint_text='Email', size_hint_y=None, height=dp(50))
        main_layout.add_widget(self.email_input)
        
        self.password_input = StyledTextInput(hint_text='Password', password=True, size_hint_y=None, height=dp(50))
        main_layout.add_widget(self.password_input)
        
        self.confirm_input = StyledTextInput(hint_text='Confirm Password', password=True, size_hint_y=None, height=dp(50))
        main_layout.add_widget(self.confirm_input)
        
        # Register button
        register_btn = RoundedButton(
            text='🎯  Create Account',
            font_size=sp(18),
            size_hint_y=None,
            height=dp(55),
            bg_color='#48BB78'
        )
        register_btn.bind(on_press=self.register)
        main_layout.add_widget(register_btn)
        
        main_layout.add_widget(BoxLayout())  # Spacer
        
        self.add_widget(main_layout)
        self.main_layout = main_layout
    
    def update_bg(self, *args):
        self.bg.pos = self.main_layout.pos
        self.bg.size = self.main_layout.size
    
    def register(self, instance):
        fullname = self.fullname_input.text.strip()
        username = self.username_input.text.strip()
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        confirm = self.confirm_input.text.strip()
        
        if not all([fullname, username, email, password, confirm]):
            self.show_popup('Error', 'Please fill all fields')
            return
        
        if password != confirm:
            self.show_popup('Error', 'Passwords do not match')
            return
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                self.show_popup('Error', 'Username or email already exists')
                cursor.close()
                conn.close()
                return
            
            # Create user
            hashed = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password, full_name) VALUES (%s, %s, %s, %s)",
                (username, email, hashed, fullname)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            self.show_popup('Success', 'Account created! Please login.')
            self.manager.current = 'login'
        else:
            self.show_popup('Error', 'Database connection failed')
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, font_size=sp(14)),
            size_hint=(0.8, 0.3)
        )
        popup.open()


class DashboardScreen(Screen):
    """Main dashboard screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.clear_widgets()
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical')
        
        with main_layout.canvas.before:
            Color(*get_color_from_hex('#1A202C'))
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Scroll view for content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Header
        app = App.get_running_app()
        user = app.current_user
        name = user.get('full_name', 'User').split()[0] if user else 'User'
        
        header = BoxLayout(size_hint_y=None, height=dp(60))
        header.add_widget(Label(
            text=f'👋 Hello, {name}!',
            font_size=sp(22),
            bold=True,
            color=get_color_from_hex('#F7FAFC'),
            halign='left'
        ))
        content.add_widget(header)
        
        content.add_widget(Label(
            text="Here's your expense summary",
            font_size=sp(14),
            color=get_color_from_hex('#A0AEC0'),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        ))
        
        # Stats grid
        stats_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(180))
        
        self.stat_total = StatCard('Total Spent', '₹0', '💰', '#667EEA')
        stats_grid.add_widget(self.stat_total)
        
        self.stat_count = StatCard('Transactions', '0', '📊', '#48BB78')
        stats_grid.add_widget(self.stat_count)
        
        self.stat_avg = StatCard('Average', '₹0', '📈', '#ED8936')
        stats_grid.add_widget(self.stat_avg)
        
        self.stat_max = StatCard('Highest', '₹0', '⬆️', '#F56565')
        stats_grid.add_widget(self.stat_max)
        
        content.add_widget(stats_grid)
        
        # Recent expenses header
        recent_header = BoxLayout(size_hint_y=None, height=dp(40))
        recent_header.add_widget(Label(
            text='📋 Recent Expenses',
            font_size=sp(16),
            bold=True,
            color=get_color_from_hex('#F7FAFC'),
            halign='left'
        ))
        content.add_widget(recent_header)
        
        # Expenses list placeholder
        self.expenses_list = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.expenses_list.bind(minimum_height=self.expenses_list.setter('height'))
        content.add_widget(self.expenses_list)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        # Bottom navigation
        nav = self.create_bottom_nav()
        main_layout.add_widget(nav)
        
        self.add_widget(main_layout)
        self.main_layout = main_layout
        self.content = content
    
    def create_bottom_nav(self):
        nav = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(10), 0])
        
        with nav.canvas.before:
            Color(*get_color_from_hex('#2D3748'))
            Rectangle(pos=nav.pos, size=nav.size)
        
        nav_items = [
            ('🏠', 'Home', 'dashboard'),
            ('💳', 'Expenses', 'expenses'),
            ('➕', 'Add', 'add_expense'),
            ('📊', 'Reports', 'reports'),
            ('👤', 'Profile', 'profile')
        ]
        
        for icon, label, screen in nav_items:
            btn = Button(
                text=f'{icon}\n{label}',
                font_size=sp(11),
                halign='center',
                background_color=(0, 0, 0, 0),
                color=get_color_from_hex('#667EEA' if screen == 'dashboard' else '#A0AEC0')
            )
            btn.bind(on_press=partial(self.navigate, screen))
            nav.add_widget(btn)
        
        return nav
    
    def navigate(self, screen, instance):
        if screen == 'profile':
            # Logout
            app = App.get_running_app()
            app.current_user = None
            self.manager.current = 'login'
        else:
            self.manager.current = screen
    
    def update_bg(self, *args):
        self.bg.pos = self.main_layout.pos
        self.bg.size = self.main_layout.size
    
    def load_data(self):
        app = App.get_running_app()
        user_id = app.current_user.get('user_id') if app.current_user else None
        
        if not user_id:
            return
        
        conn = get_db_connection()
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
            """, (user_id,))
            stats = cursor.fetchone()
            
            # Update stat cards
            if stats:
                self.update_stat_card(self.stat_total, f"₹{stats['total']:.0f}")
                self.update_stat_card(self.stat_count, str(stats['count']))
                self.update_stat_card(self.stat_avg, f"₹{stats['avg']:.0f}")
                self.update_stat_card(self.stat_max, f"₹{stats['max']:.0f}")
            
            # Get recent expenses
            cursor.execute("""
                SELECT e.*, c.category_name, c.icon
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.category_id
                WHERE e.user_id = %s
                ORDER BY e.expense_date DESC, e.created_at DESC
                LIMIT 5
            """, (user_id,))
            expenses = cursor.fetchall()
            
            # Clear and rebuild expenses list
            self.expenses_list.clear_widgets()
            
            if expenses:
                for exp in expenses:
                    card = ExpenseCard({
                        'description': exp.get('description', 'No description'),
                        'category': exp.get('category_name', 'Other'),
                        'icon': exp.get('icon', '📦'),
                        'amount': float(exp.get('amount', 0)),
                        'date': str(exp.get('expense_date', ''))
                    })
                    self.expenses_list.add_widget(card)
            else:
                self.expenses_list.add_widget(Label(
                    text='No expenses yet\nTap + to add one!',
                    font_size=sp(14),
                    color=get_color_from_hex('#A0AEC0'),
                    halign='center',
                    size_hint_y=None,
                    height=dp(100)
                ))
            
            cursor.close()
            conn.close()
    
    def update_stat_card(self, card, value):
        """Update stat card value"""
        for child in card.children:
            if isinstance(child, Label) and child.font_size == sp(22):
                child.text = value
                break


class AddExpenseScreen(Screen):
    """Add expense screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categories = []
    
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
        self.load_categories()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        with main_layout.canvas.before:
            Color(*get_color_from_hex('#1A202C'))
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50))
        back_btn = Button(
            text='←',
            font_size=sp(24),
            size_hint_x=None,
            width=dp(50),
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex('#F7FAFC')
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        header.add_widget(Label(
            text='➕ Add Expense',
            font_size=sp(20),
            bold=True,
            color=get_color_from_hex('#F7FAFC')
        ))
        header.add_widget(BoxLayout(size_hint_x=None, width=dp(50)))
        main_layout.add_widget(header)
        
        # Amount
        main_layout.add_widget(Label(
            text='💰 Amount',
            font_size=sp(14),
            color=get_color_from_hex('#A0AEC0'),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        ))
        
        amount_box = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        amount_box.add_widget(Label(
            text='₹',
            font_size=sp(28),
            color=get_color_from_hex('#667EEA'),
            size_hint_x=None,
            width=dp(40)
        ))
        self.amount_input = StyledTextInput(
            hint_text='0.00',
            input_filter='float',
            font_size=sp(24)
        )
        amount_box.add_widget(self.amount_input)
        main_layout.add_widget(amount_box)
        
        # Category
        main_layout.add_widget(Label(
            text='📁 Category',
            font_size=sp(14),
            color=get_color_from_hex('#A0AEC0'),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        ))
        
        self.category_spinner = Spinner(
            text='Select category...',
            values=[],
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#2D3748'),
            color=get_color_from_hex('#F7FAFC')
        )
        main_layout.add_widget(self.category_spinner)
        
        # Description
        main_layout.add_widget(Label(
            text='📝 Description',
            font_size=sp(14),
            color=get_color_from_hex('#A0AEC0'),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        ))
        self.desc_input = StyledTextInput(
            hint_text='What did you spend on?',
            size_hint_y=None,
            height=dp(50)
        )
        main_layout.add_widget(self.desc_input)
        
        # Payment method
        main_layout.add_widget(Label(
            text='💳 Payment Method',
            font_size=sp(14),
            color=get_color_from_hex('#A0AEC0'),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        ))
        
        self.payment_spinner = Spinner(
            text='Cash',
            values=['Cash', 'UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Other'],
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#2D3748'),
            color=get_color_from_hex('#F7FAFC')
        )
        main_layout.add_widget(self.payment_spinner)
        
        # Spacer
        main_layout.add_widget(BoxLayout())
        
        # Save button
        save_btn = RoundedButton(
            text='✓ Save Expense',
            font_size=sp(18),
            size_hint_y=None,
            height=dp(55),
            bg_color='#48BB78'
        )
        save_btn.bind(on_press=self.save_expense)
        main_layout.add_widget(save_btn)
        
        self.add_widget(main_layout)
        self.main_layout = main_layout
    
    def update_bg(self, *args):
        self.bg.pos = self.main_layout.pos
        self.bg.size = self.main_layout.size
    
    def load_categories(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categories ORDER BY category_name")
            self.categories = cursor.fetchall()
            cursor.close()
            conn.close()
            
            self.category_spinner.values = [c['category_name'] for c in self.categories]
    
    def save_expense(self, instance):
        amount = self.amount_input.text.strip()
        category_name = self.category_spinner.text
        description = self.desc_input.text.strip()
        payment = self.payment_spinner.text
        
        if not amount or amount == '0.00':
            self.show_popup('Error', 'Please enter an amount')
            return
        
        if category_name == 'Select category...':
            self.show_popup('Error', 'Please select a category')
            return
        
        # Find category ID
        category_id = None
        for c in self.categories:
            if c['category_name'] == category_name:
                category_id = c['category_id']
                break
        
        app = App.get_running_app()
        user_id = app.current_user.get('user_id')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expenses (user_id, category_id, amount, description, 
                                     expense_date, payment_method)
                VALUES (%s, %s, %s, %s, CURRENT_DATE(), %s)
            """, (user_id, category_id, float(amount), description, payment))
            conn.commit()
            cursor.close()
            conn.close()
            
            self.show_popup('Success', 'Expense saved!')
            self.manager.current = 'dashboard'
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, font_size=sp(14)),
            size_hint=(0.8, 0.3)
        )
        popup.open()


class ExpensesScreen(Screen):
    """All expenses list screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
        self.load_expenses()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical')
        
        with main_layout.canvas.before:
            Color(*get_color_from_hex('#1A202C'))
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(20), dp(10)])
        header.add_widget(Label(
            text='💳 My Expenses',
            font_size=sp(22),
            bold=True,
            color=get_color_from_hex('#F7FAFC'),
            halign='left'
        ))
        main_layout.add_widget(header)
        
        # Scroll view
        scroll = ScrollView()
        self.expenses_list = BoxLayout(
            orientation='vertical', 
            padding=[dp(20), dp(10)], 
            spacing=dp(10), 
            size_hint_y=None
        )
        self.expenses_list.bind(minimum_height=self.expenses_list.setter('height'))
        scroll.add_widget(self.expenses_list)
        main_layout.add_widget(scroll)
        
        # Bottom nav
        nav = self.create_bottom_nav()
        main_layout.add_widget(nav)
        
        self.add_widget(main_layout)
        self.main_layout = main_layout
    
    def create_bottom_nav(self):
        nav = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(10), 0])
        
        with nav.canvas.before:
            Color(*get_color_from_hex('#2D3748'))
            Rectangle(pos=nav.pos, size=nav.size)
        
        nav_items = [
            ('🏠', 'Home', 'dashboard'),
            ('💳', 'Expenses', 'expenses'),
            ('➕', 'Add', 'add_expense'),
            ('📊', 'Reports', 'reports'),
            ('👤', 'Profile', 'profile')
        ]
        
        for icon, label, screen in nav_items:
            btn = Button(
                text=f'{icon}\n{label}',
                font_size=sp(11),
                halign='center',
                background_color=(0, 0, 0, 0),
                color=get_color_from_hex('#667EEA' if screen == 'expenses' else '#A0AEC0')
            )
            btn.bind(on_press=partial(self.navigate, screen))
            nav.add_widget(btn)
        
        return nav
    
    def navigate(self, screen, instance):
        if screen == 'profile':
            app = App.get_running_app()
            app.current_user = None
            self.manager.current = 'login'
        else:
            self.manager.current = screen
    
    def update_bg(self, *args):
        self.bg.pos = self.main_layout.pos
        self.bg.size = self.main_layout.size
    
    def load_expenses(self):
        app = App.get_running_app()
        user_id = app.current_user.get('user_id') if app.current_user else None
        
        if not user_id:
            return
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT e.*, c.category_name, c.icon
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.category_id
                WHERE e.user_id = %s
                ORDER BY e.expense_date DESC, e.created_at DESC
            """, (user_id,))
            expenses = cursor.fetchall()
            cursor.close()
            conn.close()
            
            self.expenses_list.clear_widgets()
            
            if expenses:
                for exp in expenses:
                    card = ExpenseCard({
                        'description': exp.get('description', 'No description'),
                        'category': exp.get('category_name', 'Other'),
                        'icon': exp.get('icon', '📦'),
                        'amount': float(exp.get('amount', 0)),
                        'date': str(exp.get('expense_date', ''))
                    })
                    self.expenses_list.add_widget(card)
            else:
                self.expenses_list.add_widget(Label(
                    text='No expenses found',
                    font_size=sp(16),
                    color=get_color_from_hex('#A0AEC0'),
                    size_hint_y=None,
                    height=dp(100)
                ))


class ReportsScreen(Screen):
    """Reports screen with simple stats"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical')
        
        with main_layout.canvas.before:
            Color(*get_color_from_hex('#1A202C'))
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(20), dp(10)])
        header.add_widget(Label(
            text='📊 Reports',
            font_size=sp(22),
            bold=True,
            color=get_color_from_hex('#F7FAFC'),
            halign='left'
        ))
        main_layout.add_widget(header)
        
        # Content scroll
        scroll = ScrollView()
        self.content = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(10)],
            spacing=dp(15),
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        main_layout.add_widget(scroll)
        
        # Bottom nav
        nav = self.create_bottom_nav()
        main_layout.add_widget(nav)
        
        self.add_widget(main_layout)
        self.main_layout = main_layout
    
    def create_bottom_nav(self):
        nav = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(10), 0])
        
        with nav.canvas.before:
            Color(*get_color_from_hex('#2D3748'))
            Rectangle(pos=nav.pos, size=nav.size)
        
        nav_items = [
            ('🏠', 'Home', 'dashboard'),
            ('💳', 'Expenses', 'expenses'),
            ('➕', 'Add', 'add_expense'),
            ('📊', 'Reports', 'reports'),
            ('👤', 'Profile', 'profile')
        ]
        
        for icon, label, screen in nav_items:
            btn = Button(
                text=f'{icon}\n{label}',
                font_size=sp(11),
                halign='center',
                background_color=(0, 0, 0, 0),
                color=get_color_from_hex('#667EEA' if screen == 'reports' else '#A0AEC0')
            )
            btn.bind(on_press=partial(self.navigate, screen))
            nav.add_widget(btn)
        
        return nav
    
    def navigate(self, screen, instance):
        if screen == 'profile':
            app = App.get_running_app()
            app.current_user = None
            self.manager.current = 'login'
        else:
            self.manager.current = screen
    
    def update_bg(self, *args):
        self.bg.pos = self.main_layout.pos
        self.bg.size = self.main_layout.size
    
    def load_data(self):
        app = App.get_running_app()
        user_id = app.current_user.get('user_id') if app.current_user else None
        
        if not user_id:
            return
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get category totals
            cursor.execute("""
                SELECT c.category_name, c.icon, c.color, SUM(e.amount) as total
                FROM expenses e
                JOIN categories c ON e.category_id = c.category_id
                WHERE e.user_id = %s AND MONTH(e.expense_date) = MONTH(CURRENT_DATE())
                GROUP BY c.category_id
                ORDER BY total DESC
            """, (user_id,))
            categories = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            self.content.clear_widgets()
            
            # Total card
            total = sum(float(c['total']) for c in categories) if categories else 0
            total_card = StatCard('Total This Month', f'₹{total:.0f}', '💰', '#667EEA')
            total_card.size_hint_y = None
            total_card.height = dp(90)
            self.content.add_widget(total_card)
            
            # Category breakdown
            self.content.add_widget(Label(
                text='Category Breakdown',
                font_size=sp(16),
                bold=True,
                color=get_color_from_hex('#F7FAFC'),
                halign='left',
                size_hint_y=None,
                height=dp(40)
            ))
            
            if categories:
                for cat in categories:
                    pct = (float(cat['total']) / total * 100) if total > 0 else 0
                    
                    cat_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
                    
                    cat_box.add_widget(Label(
                        text=cat.get('icon', '📦'),
                        font_size=sp(20),
                        size_hint_x=None,
                        width=dp(35)
                    ))
                    
                    info = BoxLayout(orientation='vertical')
                    info.add_widget(Label(
                        text=cat['category_name'],
                        font_size=sp(14),
                        color=get_color_from_hex('#F7FAFC'),
                        halign='left',
                        text_size=(dp(150), None)
                    ))
                    info.add_widget(Label(
                        text=f'{pct:.1f}%',
                        font_size=sp(11),
                        color=get_color_from_hex('#A0AEC0'),
                        halign='left',
                        text_size=(dp(150), None)
                    ))
                    cat_box.add_widget(info)
                    
                    cat_box.add_widget(Label(
                        text=f'₹{float(cat["total"]):.0f}',
                        font_size=sp(16),
                        bold=True,
                        color=get_color_from_hex('#F56565'),
                        size_hint_x=None,
                        width=dp(80)
                    ))
                    
                    self.content.add_widget(cat_box)
            else:
                self.content.add_widget(Label(
                    text='No data available',
                    font_size=sp(14),
                    color=get_color_from_hex('#A0AEC0'),
                    size_hint_y=None,
                    height=dp(50)
                ))


class ExpenseTrackerApp(App):
    """Main Kivy Application"""
    current_user = None
    
    def build(self):
        self.title = 'Expense Tracker'
        
        # Screen manager
        sm = ScreenManager(transition=SlideTransition())
        
        # Add screens
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(AddExpenseScreen(name='add_expense'))
        sm.add_widget(ExpensesScreen(name='expenses'))
        sm.add_widget(ReportsScreen(name='reports'))
        
        return sm


if __name__ == '__main__':
    ExpenseTrackerApp().run()
