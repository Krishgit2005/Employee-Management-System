from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee') # 'admin' or 'employee'
    
    # Profile details
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    position = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    base_salary = db.Column(db.Float, nullable=True, default=0.0)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    salaries = db.relationship('Salary', backref='employee', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.String(20), nullable=False) # 'Present', 'Absent', 'Leave', 'Half-day'

class Salary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False) # e.g., '2025-01'
    amount_paid = db.Column(db.Float, nullable=False)
    deductions = db.Column(db.Float, nullable=False, default=0.0)
    payment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending') # 'Pending', 'Approved', 'Rejected'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    employee = db.relationship('User', backref=db.backref('leaves', lazy='dynamic'))
