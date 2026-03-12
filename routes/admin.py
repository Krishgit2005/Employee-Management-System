from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import db, User, Attendance, Salary, LeaveRequest
from routes.decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.filter_by(role='employee').all()
    emp_count = len(users)
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
    return render_template('admin/dashboard.html', users=users, emp_count=emp_count, pending_leaves=pending_leaves)

@bp.route('/attendance')
@login_required
@admin_required
def attendance_report():
    users = User.query.filter_by(role='employee').all()
    from datetime import datetime
    today = datetime.utcnow().date()
    # Get today's attendance for all users
    today_records = Attendance.query.filter_by(date=today).all()
    marked_ids = {r.employee_id for r in today_records}
    
    return render_template('admin/attendance_report.html', users=users, marked_ids=marked_ids, date=today)

@bp.route('/employee/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    if request.method == 'POST':
        try:
            new_emp = User(
                username=request.form['username'],
                role='employee',
                full_name=request.form['full_name'],
                email=request.form['email'],
                position=request.form['position'],
                department=request.form['department'],
                base_salary=float(request.form['base_salary'] or 0)
            )
            new_emp.set_password(request.form['password'])
            db.session.add(new_emp)
            db.session.commit()
            flash('Employee added successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'Error adding employee: {str(e)}', 'error')
            
    return render_template('admin/employee_form.html', action='Add', user=None)

@bp.route('/employee/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        try:
            user.username = request.form['username']
            user.full_name = request.form['full_name']
            user.email = request.form['email']
            user.position = request.form['position']
            user.department = request.form['department']
            user.base_salary = float(request.form['base_salary'] or 0)
            
            if request.form['password']:  # Only update if provided
                user.set_password(request.form['password'])
                
            db.session.commit()
            flash('Employee updated successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'Error updating employee: {str(e)}', 'error')
            
    return render_template('admin/employee_form.html', action='Edit', user=user)

@bp.route('/employee/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_employee(id):
    user = User.query.get_or_404(id)
    if user.role != 'admin': # Prevent deleting admins from here
        db.session.delete(user)
        db.session.commit()
        flash('Employee deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@bp.route('/employee/<int:id>/analysis')
@login_required
@admin_required
def analysis(id):
    user = User.query.get_or_404(id)
    attendances = Attendance.query.filter_by(employee_id=id).order_by(Attendance.date.desc()).limit(30).all()
    salaries = Salary.query.filter_by(employee_id=id).order_by(Salary.month.desc()).all()
    return render_template('admin/analysis.html', user=user, attendances=attendances, salaries=salaries)

@bp.route('/leaves')
@login_required
@admin_required
def manage_leaves():
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').order_by(LeaveRequest.created_at.asc()).all()
    all_leaves = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).limit(50).all()
    return render_template('admin/leaves.html', pending_leaves=pending_leaves, all_leaves=all_leaves)

@bp.route('/leave/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_leave(id):
    leave = LeaveRequest.query.get_or_404(id)
    leave.status = 'Approved'
    db.session.commit()
    flash(f'Leave request for {leave.employee.full_name} approved.', 'success')
    return redirect(url_for('admin.manage_leaves'))

@bp.route('/leave/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_leave(id):
    leave = LeaveRequest.query.get_or_404(id)
    leave.status = 'Rejected'
    db.session.commit()
    flash(f'Leave request for {leave.employee.full_name} rejected.', 'error')
    return redirect(url_for('admin.manage_leaves'))

@bp.route('/employee/<int:id>/payroll', methods=['GET', 'POST'])
@login_required
@admin_required
def process_payroll(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        try:
            month = request.form['month'] # Format: YYYY-MM
            
            # Validation: Prevent duplicate payroll for the same month
            existing = Salary.query.filter_by(employee_id=id, month=month).first()
            if existing:
                flash(f'Payroll already processed for {user.full_name} for {month}.', 'warning')
                return redirect(url_for('admin.analysis', id=id))

            deductions = float(request.form['deductions'] or 0)
            amount_paid = user.base_salary - deductions
            
            new_salary = Salary(
                employee_id=id,
                month=month,
                amount_paid=amount_paid,
                deductions=deductions
            )
            db.session.add(new_salary)
            db.session.commit()
            flash(f'Payroll processed successfully for {user.full_name}.', 'success')
            return redirect(url_for('admin.analysis', id=id))
        except Exception as e:
            flash(f'Error processing payroll: {str(e)}', 'error')
            
    return render_template('admin/payroll_form.html', user=user)
