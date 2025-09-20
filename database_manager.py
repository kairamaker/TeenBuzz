#!/usr/bin/env python3

import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

class LocalDatabase:
    """Local SQLite database manager that mimics Supabase functionality"""
    
    def __init__(self, db_path: str = 'teenbuzz_local.db'):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to the local database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        return self
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        # Convert rows to dictionaries
        columns = [description[0] for description in cursor.description] if cursor.description else []
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        self.conn.commit()
        return results
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into a table"""
        if not self.conn:
            self.connect()
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(data.values()))
        
        # Get the inserted row ID
        row_id = cursor.lastrowid
        
        self.conn.commit()
        
        # Return the inserted data with ID
        data['id'] = row_id
        return data
    
    def select(self, table: str, columns: str = '*', where: str = '', params: tuple = (), limit: int = None) -> List[Dict[str, Any]]:
        """Select data from a table"""
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, params)
    
    def update(self, table: str, data: Dict[str, Any], where: str, params: tuple = ()) -> int:
        """Update data in a table"""
        if not self.conn:
            self.connect()
        
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(data.values()) + params)
        
        self.conn.commit()
        return cursor.rowcount
    
    def delete(self, table: str, where: str, params: tuple = ()) -> int:
        """Delete data from a table"""
        if not self.conn:
            self.connect()
        
        query = f"DELETE FROM {table} WHERE {where}"
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        self.conn.commit()
        return cursor.rowcount

class DatabaseToggle:
    """Toggle between local and cloud databases"""
    
    def __init__(self):
        self.config_file = 'database_config.json'
        self.load_config()
    
    def load_config(self):
        """Load database configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'use_local': True,
                'local_db_path': 'teenbuzz_local.db',
                'supabase_url': os.getenv('SUPABASE_URL', ''),
                'supabase_key': os.getenv('SUPABASE_KEY', '')
            }
            self.save_config()
    
    def save_config(self):
        """Save database configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def use_local(self):
        """Switch to local database"""
        self.config['use_local'] = True
        self.save_config()
        print("✅ Switched to LOCAL database")
    
    def use_cloud(self):
        """Switch to cloud database"""
        self.config['use_local'] = False
        self.save_config()
        print("✅ Switched to CLOUD database")
    
    def get_database(self):
        """Get the appropriate database instance"""
        if self.config['use_local']:
            return LocalDatabase(self.config['local_db_path'])
        else:
            # Return None to use Supabase (handled in app.py)
            return None
    
    def get_status(self):
        """Get current database status"""
        if self.config['use_local']:
            return "LOCAL (SQLite)"
        else:
            return "CLOUD (Supabase)"

# Convenience functions
def get_database():
    """Get the current database instance"""
    toggle = DatabaseToggle()
    return toggle.get_database()

def switch_to_local():
    """Switch to local database"""
    toggle = DatabaseToggle()
    toggle.use_local()

def switch_to_cloud():
    """Switch to cloud database"""
    toggle = DatabaseToggle()
    toggle.use_cloud()

def get_database_status():
    """Get current database status"""
    toggle = DatabaseToggle()
    return toggle.get_status()

if __name__ == "__main__":
    # Test the database toggle
    print("=== Database Toggle Test ===")
    
    toggle = DatabaseToggle()
    print(f"Current database: {toggle.get_status()}")
    
    # Test local database
    with LocalDatabase() as db:
        articles = db.select('articles', limit=3)
        print(f"Found {len(articles)} articles in local database")
        if articles:
            print(f"Sample article: {articles[0]['headline']}")
