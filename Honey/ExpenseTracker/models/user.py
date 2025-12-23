"""
User Model
Handles user-related database operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import get_db
from utils.helpers import hash_password, verify_password


class User:
    """User model class"""
    
    def __init__(self, user_id=None, username=None, email=None, 
                 full_name=None, created_at=None, is_active=True):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.created_at = created_at
        self.is_active = is_active
    
    @staticmethod
    def create(username, email, password, full_name):
        """Create a new user"""
        db = get_db()
        hashed_password = hash_password(password)
        
        query = """
            INSERT INTO users (username, email, password, full_name)
            VALUES (%s, %s, %s, %s)
        """
        
        try:
            user_id = db.execute_query(query, (username, email, hashed_password, full_name), fetch=False)
            if user_id:
                return User(user_id=user_id, username=username, 
                           email=email, full_name=full_name)
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user with username and password"""
        db = get_db()
        
        query = """
            SELECT user_id, username, email, password, full_name, created_at, is_active
            FROM users
            WHERE (username = %s OR email = %s) AND is_active = TRUE
        """
        
        result = db.execute_query(query, (username, username))
        
        if result and len(result) > 0:
            user_data = result[0]
            if verify_password(password, user_data['password']):
                return User(
                    user_id=user_data['user_id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    created_at=user_data['created_at'],
                    is_active=user_data['is_active']
                )
        return None
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        db = get_db()
        
        query = """
            SELECT user_id, username, email, full_name, created_at, is_active
            FROM users
            WHERE user_id = %s
        """
        
        result = db.execute_query(query, (user_id,))
        
        if result and len(result) > 0:
            user_data = result[0]
            return User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                created_at=user_data['created_at'],
                is_active=user_data['is_active']
            )
        return None
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        db = get_db()
        
        query = """
            SELECT user_id, username, email, full_name, created_at, is_active
            FROM users
            WHERE username = %s
        """
        
        result = db.execute_query(query, (username,))
        
        if result and len(result) > 0:
            user_data = result[0]
            return User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                created_at=user_data['created_at'],
                is_active=user_data['is_active']
            )
        return None
    
    @staticmethod
    def exists(username=None, email=None):
        """Check if username or email already exists"""
        db = get_db()
        
        if username:
            query = "SELECT COUNT(*) as count FROM users WHERE username = %s"
            result = db.execute_query(query, (username,))
            if result and result[0]['count'] > 0:
                return True, 'username'
        
        if email:
            query = "SELECT COUNT(*) as count FROM users WHERE email = %s"
            result = db.execute_query(query, (email,))
            if result and result[0]['count'] > 0:
                return True, 'email'
        
        return False, None
    
    def update(self, full_name=None, email=None):
        """Update user information"""
        db = get_db()
        
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = %s")
            params.append(full_name)
        
        if email:
            updates.append("email = %s")
            params.append(email)
        
        if not updates:
            return False
        
        params.append(self.user_id)
        
        query = f"""
            UPDATE users
            SET {', '.join(updates)}
            WHERE user_id = %s
        """
        
        result = db.execute_query(query, tuple(params), fetch=False)
        return result is not None
    
    def change_password(self, old_password, new_password):
        """Change user password"""
        db = get_db()
        
        # Verify old password
        query = "SELECT password FROM users WHERE user_id = %s"
        result = db.execute_query(query, (self.user_id,))
        
        if not result or not verify_password(old_password, result[0]['password']):
            return False, "Current password is incorrect"
        
        # Update password
        new_hashed = hash_password(new_password)
        update_query = "UPDATE users SET password = %s WHERE user_id = %s"
        result = db.execute_query(update_query, (new_hashed, self.user_id), fetch=False)
        
        if result is not None:
            return True, "Password changed successfully"
        return False, "Failed to update password"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at,
            'is_active': self.is_active
        }
