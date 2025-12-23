"""
Authentication Controller
Handles login, registration, and session management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User
from utils.helpers import validate_email, validate_username, validate_password


class AuthController:
    """Authentication controller class"""
    
    _current_user = None
    
    @classmethod
    def login(cls, username, password):
        """
        Authenticate user
        Returns: (success, message, user)
        """
        if not username or not password:
            return False, "Please enter username and password", None
        
        user = User.authenticate(username, password)
        
        if user:
            cls._current_user = user
            return True, f"Welcome back, {user.full_name}!", user
        else:
            return False, "Invalid username or password", None
    
    @classmethod
    def register(cls, username, email, password, confirm_password, full_name):
        """
        Register new user
        Returns: (success, message, user)
        """
        # Validate inputs
        if not all([username, email, password, confirm_password, full_name]):
            return False, "All fields are required", None
        
        # Validate username
        if not validate_username(username):
            return False, "Username must be 3-20 characters (letters, numbers, underscore)", None
        
        # Validate email
        if not validate_email(email):
            return False, "Please enter a valid email address", None
        
        # Validate password
        valid, msg = validate_password(password)
        if not valid:
            return False, msg, None
        
        # Check password match
        if password != confirm_password:
            return False, "Passwords do not match", None
        
        # Check if username or email exists
        exists, field = User.exists(username=username, email=email)
        if exists:
            if field == 'username':
                return False, "Username already taken", None
            else:
                return False, "Email already registered", None
        
        # Create user
        user = User.create(username, email, password, full_name)
        
        if user:
            cls._current_user = user
            return True, "Registration successful! Welcome!", user
        else:
            return False, "Registration failed. Please try again.", None
    
    @classmethod
    def logout(cls):
        """Log out current user"""
        cls._current_user = None
        return True, "Logged out successfully"
    
    @classmethod
    def get_current_user(cls):
        """Get currently logged in user"""
        return cls._current_user
    
    @classmethod
    def is_logged_in(cls):
        """Check if user is logged in"""
        return cls._current_user is not None
    
    @classmethod
    def update_profile(cls, full_name=None, email=None):
        """Update current user's profile"""
        if not cls._current_user:
            return False, "Not logged in"
        
        if email and not validate_email(email):
            return False, "Please enter a valid email address"
        
        if email and email != cls._current_user.email:
            exists, _ = User.exists(email=email)
            if exists:
                return False, "Email already registered"
        
        success = cls._current_user.update(full_name=full_name, email=email)
        
        if success:
            if full_name:
                cls._current_user.full_name = full_name
            if email:
                cls._current_user.email = email
            return True, "Profile updated successfully"
        
        return False, "Failed to update profile"
    
    @classmethod
    def change_password(cls, old_password, new_password, confirm_password):
        """Change current user's password"""
        if not cls._current_user:
            return False, "Not logged in"
        
        if new_password != confirm_password:
            return False, "New passwords do not match"
        
        valid, msg = validate_password(new_password)
        if not valid:
            return False, msg
        
        success, message = cls._current_user.change_password(old_password, new_password)
        return success, message
