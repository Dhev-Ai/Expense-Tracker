"""
Enhanced Login View
Modern login with remember me, animations, and better UX
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import COLORS, FONTS, DIMENSIONS
from controllers.auth_controller import AuthController


# Path to save login credentials
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'saved_login.json')


class LoginView(tk.Frame):
    """Enhanced Login and Registration View"""
    
    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg=COLORS['bg_secondary'])
        self.parent = parent
        self.on_login_success = on_login_success
        self.is_login_mode = True
        self.remember_var = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_saved_credentials()
    
    def load_saved_credentials(self):
        """Load saved login credentials if remember me was checked"""
        try:
            if os.path.exists(CREDENTIALS_FILE):
                with open(CREDENTIALS_FILE, 'r') as f:
                    data = json.load(f)
                    if data.get('remember') and self.is_login_mode:
                        saved_username = data.get('username', '')
                        saved_password = data.get('password', '')
                        
                        if saved_username:
                            # Clear placeholder and insert saved username
                            self.username_entry.delete(0, tk.END)
                            self.username_entry.insert(0, saved_username)
                            self.username_entry.config(fg=COLORS['text_primary'])
                        
                        if saved_password:
                            # Clear placeholder and insert saved password
                            self.password_entry.delete(0, tk.END)
                            self.password_entry.insert(0, saved_password)
                            self.password_entry.config(fg=COLORS['text_primary'], show='•')
                        
                        self.remember_var.set(True)
        except Exception as e:
            print(f"Could not load saved credentials: {e}")
    
    def save_credentials(self, username, password):
        """Save login credentials"""
        try:
            os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump({
                    'username': username,
                    'password': password,
                    'remember': True
                }, f)
        except Exception as e:
            print(f"Could not save credentials: {e}")
    
    def clear_saved_credentials(self):
        """Clear saved credentials"""
        try:
            if os.path.exists(CREDENTIALS_FILE):
                os.remove(CREDENTIALS_FILE)
        except Exception as e:
            print(f"Could not clear credentials: {e}")
    
    def create_widgets(self):
        """Create login/register widgets"""
        self.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Branding with gradient effect
        left_panel = tk.Frame(self, bg=COLORS['primary'], width=500)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        # Create gradient effect with multiple frames
        gradient_colors = ['#667EEA', '#6B5CE7', '#7647E0', '#8040D8', '#764BA2']
        for i, color in enumerate(gradient_colors):
            stripe = tk.Frame(left_panel, bg=color, height=150)
            stripe.pack(fill=tk.X)
        
        # Branding overlay
        brand_frame = tk.Frame(left_panel, bg=COLORS['primary'])
        brand_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        brand_frame.configure(bg=gradient_colors[2])
        
        # Animated logo effect
        logo_container = tk.Frame(brand_frame, bg=gradient_colors[2])
        logo_container.pack(pady=(0, 20))
        
        # Logo (without shadow - Tkinter doesn't support RGBA)
        logo_label = tk.Label(
            logo_container,
            text="💰",
            font=('Segoe UI', 80),
            bg=gradient_colors[2],
            fg=COLORS['text_white']
        )
        logo_label.pack()
        
        # App name with glow
        app_name = tk.Label(
            brand_frame,
            text="Expense Tracker",
            font=FONTS['heading_xl'],
            bg=gradient_colors[2],
            fg=COLORS['text_white']
        )
        app_name.pack()
        
        # Tagline
        tagline = tk.Label(
            brand_frame,
            text="Smart Money Management",
            font=FONTS['body_large'],
            bg=gradient_colors[2],
            fg='#E2E8F0'
        )
        tagline.pack(pady=(5, 0))
        
        # Feature cards
        features_frame = tk.Frame(brand_frame, bg=gradient_colors[2])
        features_frame.pack(pady=(40, 0))
        
        features = [
            ("📊", "Track Expenses", "Monitor daily spending"),
            ("🎯", "Set Budgets", "Control your finances"),
            ("📈", "Visual Reports", "Charts & analytics"),
            ("💾", "Export Data", "Download reports"),
        ]
        
        for icon, title, desc in features:
            feat_card = tk.Frame(features_frame, bg=gradient_colors[2], padx=15, pady=10)
            feat_card.pack(fill=tk.X, pady=5)
            
            tk.Label(
                feat_card,
                text=f"{icon}  {title}",
                font=FONTS['body_medium'],
                bg=gradient_colors[2],
                fg=COLORS['text_white']
            ).pack(anchor='w')
            
            tk.Label(
                feat_card,
                text=desc,
                font=FONTS['caption'],
                bg=gradient_colors[2],
                fg='#E2E8F0'
            ).pack(anchor='w')
        
        # Right panel - Form
        right_panel = tk.Frame(self, bg=COLORS['bg_primary'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # GPS text in top right corner
        gps_label = tk.Label(
            right_panel,
            text="GPS",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_primary'],
            fg=COLORS['primary']
        )
        gps_label.place(relx=0.95, rely=0.05, anchor='ne')
        
        # Form container with shadow effect
        form_wrapper = tk.Frame(right_panel, bg=COLORS['bg_primary'])
        form_wrapper.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.form_container = tk.Frame(form_wrapper, bg=COLORS['bg_primary'])
        self.form_container.pack(padx=40, pady=40)
        
        # Create login form
        self.create_login_form()
    
    def create_login_form(self):
        """Create enhanced login form"""
        self.clear_form()
        self.is_login_mode = True
        
        # Welcome icon
        icon_label = tk.Label(
            self.form_container,
            text="👋",
            font=('Segoe UI', 48),
            bg=COLORS['bg_primary']
        )
        icon_label.pack(pady=(0, 10))
        
        # Title
        title = tk.Label(
            self.form_container,
            text="Welcome Back!",
            font=FONTS['heading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        )
        title.pack(pady=(0, 5))
        
        subtitle = tk.Label(
            self.form_container,
            text="Sign in to continue to your account",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        )
        subtitle.pack(pady=(0, 30))
        
        # Username field with icon
        self.create_input_field("👤", "Username or Email", "username")
        
        # Password field with icon
        self.create_input_field("🔒", "Password", "password", show='•')
        
        # Remember me & Forgot password row
        options_frame = tk.Frame(self.form_container, bg=COLORS['bg_primary'])
        options_frame.pack(fill=tk.X, pady=(5, 20))
        
        # Remember me checkbox
        remember_frame = tk.Frame(options_frame, bg=COLORS['bg_primary'])
        remember_frame.pack(side=tk.LEFT)
        
        self.remember_check = tk.Checkbutton(
            remember_frame,
            text=" Remember me",
            variable=self.remember_var,
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary'],
            activebackground=COLORS['bg_primary'],
            selectcolor=COLORS['bg_primary'],
            cursor='hand2'
        )
        self.remember_check.pack(side=tk.LEFT)
        
        # Login button with hover effect
        login_btn = tk.Button(
            self.form_container,
            text="🚀  Sign In",
            font=FONTS['button_large'],
            bg=COLORS['primary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['primary_dark'],
            activeforeground=COLORS['text_white'],
            relief=tk.FLAT,
            cursor='hand2',
            width=30,
            height=2,
            command=self.handle_login
        )
        login_btn.pack(pady=(10, 20))
        
        # Hover effects
        login_btn.bind('<Enter>', lambda e: login_btn.config(bg=COLORS['primary_dark']))
        login_btn.bind('<Leave>', lambda e: login_btn.config(bg=COLORS['primary']))
        
        # Bind Enter key
        self.parent.bind('<Return>', lambda e: self.handle_login())
        
        # Divider
        divider_frame = tk.Frame(self.form_container, bg=COLORS['bg_primary'])
        divider_frame.pack(fill=tk.X, pady=15)
        
        tk.Frame(divider_frame, bg=COLORS['border'], height=1).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(divider_frame, text="  OR  ", font=FONTS['caption'], bg=COLORS['bg_primary'], fg=COLORS['text_light']).pack(side=tk.LEFT)
        tk.Frame(divider_frame, bg=COLORS['border'], height=1).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Register link
        register_frame = tk.Frame(self.form_container, bg=COLORS['bg_primary'])
        register_frame.pack(pady=(10, 0))
        
        tk.Label(
            register_frame,
            text="Don't have an account?",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
        
        register_link = tk.Label(
            register_frame,
            text=" Create Account",
            font=FONTS['button'],
            bg=COLORS['bg_primary'],
            fg=COLORS['primary'],
            cursor='hand2'
        )
        register_link.pack(side=tk.LEFT)
        register_link.bind('<Button-1>', lambda e: self.create_register_form())
        register_link.bind('<Enter>', lambda e: register_link.config(fg=COLORS['primary_dark']))
        register_link.bind('<Leave>', lambda e: register_link.config(fg=COLORS['primary']))
        
        # Load saved credentials after creating entries
        self.load_saved_credentials()
    
    def create_register_form(self):
        """Create enhanced registration form"""
        self.clear_form()
        self.is_login_mode = False
        
        # Icon
        icon_label = tk.Label(
            self.form_container,
            text="🎉",
            font=('Segoe UI', 48),
            bg=COLORS['bg_primary']
        )
        icon_label.pack(pady=(0, 10))
        
        # Title
        title = tk.Label(
            self.form_container,
            text="Create Account",
            font=FONTS['heading'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary']
        )
        title.pack(pady=(0, 5))
        
        subtitle = tk.Label(
            self.form_container,
            text="Start tracking your expenses today",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        )
        subtitle.pack(pady=(0, 25))
        
        # Full name
        self.create_input_field("👤", "Full Name", "full_name")
        
        # Username
        self.create_input_field("📝", "Username", "username")
        
        # Email
        self.create_input_field("📧", "Email Address", "email")
        
        # Password
        self.create_input_field("🔒", "Password", "password", show='•')
        
        # Confirm Password
        self.create_input_field("🔐", "Confirm Password", "confirm_password", show='•')
        
        # Terms checkbox
        terms_frame = tk.Frame(self.form_container, bg=COLORS['bg_primary'])
        terms_frame.pack(fill=tk.X, pady=(10, 15))
        
        self.terms_var = tk.BooleanVar(value=True)
        terms_check = tk.Checkbutton(
            terms_frame,
            text=" I agree to the Terms & Conditions",
            variable=self.terms_var,
            font=FONTS['body_small'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary'],
            activebackground=COLORS['bg_primary'],
            selectcolor=COLORS['bg_primary'],
            cursor='hand2'
        )
        terms_check.pack(side=tk.LEFT)
        
        # Register button
        register_btn = tk.Button(
            self.form_container,
            text="🎯  Create Account",
            font=FONTS['button_large'],
            bg=COLORS['success'],
            fg=COLORS['text_white'],
            activebackground=COLORS['secondary_dark'],
            activeforeground=COLORS['text_white'],
            relief=tk.FLAT,
            cursor='hand2',
            width=30,
            height=2,
            command=self.handle_register
        )
        register_btn.pack(pady=(10, 20))
        
        register_btn.bind('<Enter>', lambda e: register_btn.config(bg='#38A169'))
        register_btn.bind('<Leave>', lambda e: register_btn.config(bg=COLORS['success']))
        
        # Bind Enter key
        self.parent.bind('<Return>', lambda e: self.handle_register())
        
        # Login link
        login_frame = tk.Frame(self.form_container, bg=COLORS['bg_primary'])
        login_frame.pack(pady=(10, 0))
        
        tk.Label(
            login_frame,
            text="Already have an account?",
            font=FONTS['body'],
            bg=COLORS['bg_primary'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT)
        
        login_link = tk.Label(
            login_frame,
            text=" Sign In",
            font=FONTS['button'],
            bg=COLORS['bg_primary'],
            fg=COLORS['primary'],
            cursor='hand2'
        )
        login_link.pack(side=tk.LEFT)
        login_link.bind('<Button-1>', lambda e: self.create_login_form())
        login_link.bind('<Enter>', lambda e: login_link.config(fg=COLORS['primary_dark']))
        login_link.bind('<Leave>', lambda e: login_link.config(fg=COLORS['primary']))
    
    def create_input_field(self, icon, placeholder, field_name, show=None):
        """Create styled input field with icon"""
        # Container
        field_frame = tk.Frame(self.form_container, bg=COLORS['bg_tertiary'], padx=15, pady=12)
        field_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Icon
        icon_label = tk.Label(
            field_frame,
            text=icon,
            font=FONTS['body_large'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_secondary']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entry
        entry = tk.Entry(
            field_frame,
            font=FONTS['body_large'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            width=30,
            show=show,
            insertbackground=COLORS['primary']
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        # Placeholder functionality
        entry.placeholder = placeholder
        entry.insert(0, placeholder)
        entry.config(fg=COLORS['text_light'])
        
        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=COLORS['text_primary'])
                if show:
                    entry.config(show=show)
            field_frame.config(bg=COLORS['primary_light'])
            icon_label.config(bg=COLORS['primary_light'])
            entry.config(bg=COLORS['primary_light'])
        
        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=COLORS['text_light'], show='')
            field_frame.config(bg=COLORS['bg_tertiary'])
            icon_label.config(bg=COLORS['bg_tertiary'])
            entry.config(bg=COLORS['bg_tertiary'])
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        
        # Store reference
        setattr(self, f'{field_name}_entry', entry)
    
    def get_entry_value(self, entry):
        """Get entry value, ignoring placeholder"""
        value = entry.get()
        if hasattr(entry, 'placeholder') and value == entry.placeholder:
            return ''
        return value.strip()
    
    def clear_form(self):
        """Clear form container"""
        for widget in self.form_container.winfo_children():
            widget.destroy()
    
    def handle_login(self):
        """Handle login button click"""
        username = self.get_entry_value(self.username_entry)
        password = self.get_entry_value(self.password_entry)
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        success, message, user = AuthController.login(username, password)
        
        if success:
            # Save credentials if remember me is checked
            if self.remember_var.get():
                self.save_credentials(username, password)
            else:
                self.clear_saved_credentials()
            
            self.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", message)
    
    def handle_register(self):
        """Handle register button click"""
        full_name = self.get_entry_value(self.full_name_entry)
        username = self.get_entry_value(self.username_entry)
        email = self.get_entry_value(self.email_entry)
        password = self.get_entry_value(self.password_entry)
        confirm_password = self.get_entry_value(self.confirm_password_entry)
        
        if not self.terms_var.get():
            messagebox.showerror("Error", "Please accept the Terms & Conditions")
            return
        
        success, message, user = AuthController.register(
            username, email, password, confirm_password, full_name
        )
        
        if success:
            messagebox.showinfo("🎉 Success", f"Welcome to Expense Tracker, {full_name}!")
            self.on_login_success(user)
        else:
            messagebox.showerror("Registration Failed", message)
