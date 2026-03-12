from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Attendance, Salary, LeaveRequest
from routes.decorators import employee_required
from datetime import datetime

bp = Blueprint('employee', __name__, url_prefix='/employee')

@bp.route('/dashboard')
@login_required
@employee_required
def dashboard():
    attendances = Attendance.query.filter_by(employee_id=current_user.id).order_by(Attendance.date.desc()).limit(15).all()
    salaries = Salary.query.filter_by(employee_id=current_user.id).order_by(Salary.month.desc()).all()
    
    # Calculate some stats
    total_present = Attendance.query.filter_by(employee_id=current_user.id, status='Present').count()
    
    return render_template('employee/dashboard.html', 
                          attendances=attendances, 
                          salaries=salaries,
                          total_present=total_present)

@bp.route('/salary/<int:id>')
@login_required
@employee_required
def view_salary_slip(id):
    salary = Salary.query.get_or_404(id)
    if salary.employee_id != current_user.id:
        flash('Unauthorized access to salary slip.', 'error')
        return redirect(url_for('employee.dashboard'))
    return render_template('employee/salary_slip.html', salary=salary)

@bp.route('/mark-attendance', methods=['POST'])
@login_required
@employee_required
def mark_attendance():
    from datetime import datetime
    today = datetime.utcnow().date()
    
    # Check if already marked today
    existing = Attendance.query.filter_by(employee_id=current_user.id, date=today).first()
    
    if existing:
        flash('Attendance already marked for today.', 'error')
    else:
        new_att = Attendance(employee_id=current_user.id, date=today, status='Present')
        db.session.add(new_att)
        db.session.commit()
        flash('Attendance marked as Present for today!', 'success')
        
    return redirect(url_for('employee.dashboard'))

@bp.route('/leaves')
@login_required
@employee_required
def view_leaves():
    leaves = LeaveRequest.query.filter_by(employee_id=current_user.id).order_by(LeaveRequest.created_at.desc()).all()
    return render_template('employee/leaves.html', leaves=leaves)

@bp.route('/apply-leave', methods=['GET', 'POST'])
@login_required
@employee_required
def apply_leave():
    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            reason = request.form['reason']
            
            if start_date > end_date:
                flash('Start date cannot be after end date.', 'error')
            else:
                new_leave = LeaveRequest(
                    employee_id=current_user.id,
                    start_date=start_date,
                    end_date=end_date,
                    reason=reason
                )
                db.session.add(new_leave)
                db.session.commit()
                flash('Leave request submitted successfully!', 'success')
                return redirect(url_for('employee.view_leaves'))
        except Exception as e:
            flash(f'Error submitting leave request: {str(e)}', 'error')
            
    return render_template('employee/apply_leave.html')
