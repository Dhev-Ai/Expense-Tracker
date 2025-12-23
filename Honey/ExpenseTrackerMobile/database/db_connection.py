"""
Database Connection Handler
Manages MySQL database connections and operations
"""

import mysql.connector
from mysql.connector import Error, pooling
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_config import DB_CONFIG, POOL_CONFIG


class DatabaseConnection:
    """Singleton class to manage database connections"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            self._create_pool()
    
    def _create_pool(self):
        """Create a connection pool"""
        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name=POOL_CONFIG['pool_name'],
                pool_size=POOL_CONFIG['pool_size'],
                pool_reset_session=POOL_CONFIG['pool_reset_session'],
                **DB_CONFIG
            )
            print("✅ Database connection pool created successfully!")
        except Error as e:
            print(f"❌ Error creating connection pool: {e}")
            self._pool = None
    
    def get_connection(self):
        """Get a connection from the pool"""
        try:
            if self._pool:
                return self._pool.get_connection()
            else:
                # Fallback to direct connection
                return mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            print(f"❌ Error getting connection: {e}")
            return None
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if connection is None:
                return None
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return cursor.lastrowid
                
        except Error as e:
            print(f"❌ Query execution error: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_many(self, query, data_list):
        """Execute multiple inserts"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if connection is None:
                return False
            
            cursor = connection.cursor()
            cursor.executemany(query, data_list)
            connection.commit()
            return True
            
        except Error as e:
            print(f"❌ Batch execution error: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def call_procedure(self, proc_name, params=None):
        """Call a stored procedure"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if connection is None:
                return None
            
            cursor = connection.cursor(dictionary=True)
            cursor.callproc(proc_name, params or ())
            
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            
            return results
            
        except Error as e:
            print(f"❌ Procedure call error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def test_connection(self):
        """Test database connection"""
        try:
            connection = self.get_connection()
            if connection and connection.is_connected():
                db_info = connection.get_server_info()
                print(f"✅ Connected to MySQL Server version {db_info}")
                connection.close()
                return True
            return False
        except Error as e:
            print(f"❌ Connection test failed: {e}")
            return False


# Create global database instance
db = DatabaseConnection()


def get_db():
    """Get database instance"""
    return db


def test_database():
    """Test database connection"""
    return db.test_connection()


if __name__ == "__main__":
    # Test the connection
    if test_database():
        print("Database connection successful!")
    else:
        print("Database connection failed!")
