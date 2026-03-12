import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = 'database.db'

def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # --- Employees Table ---
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    dummy_employees = [
        ('Alice Smith', 'alice@example.com', 'Software Engineer', 'Engineering', 'Active'),
        ('Bob Jones', 'bob@example.com', 'Product Manager', 'Product', 'Active'),
        ('Charlie Brown', 'charlie@example.com', 'UX Designer', 'Design', 'Inactive')
    ]
    cursor.executemany('''
        INSERT INTO employees (name, email, role, department, status)
        VALUES (?, ?, ?, ?, ?)
    ''', dummy_employees)

    # --- Users Table ---
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Create default Admin and User
    admin_hash = generate_password_hash('admin')
    user_hash = generate_password_hash('user')
    
    cursor.executemany('''
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
    ''', [
        ('admin', admin_hash, 'admin'),
        ('user', user_hash, 'user')
    ])
    
    conn.commit()
    conn.close()
    print("Database initialized successfully with Users and Employees.")

if __name__ == '__main__':
    init_db()
