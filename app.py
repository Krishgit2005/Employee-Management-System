import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_required
from models import db, User

app = Flask(__name__)
# Use a strong secret key for sessions
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ems.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Initialize database and default admin
with app.app_context():
    db.create_all()
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        new_admin = User(
            username='admin',
            role='admin',
            full_name='System Administrator',
            email='admin@ems.local',
            position='Admin',
            department='IT',
            base_salary=0.0
        )
        new_admin.set_password('admin123')
        db.session.add(new_admin)
        db.session.commit()
        print("Created default admin user (admin / admin123)")

# Basic routes will go here (imported from other files or defined below)
from routes import auth, admin, employee

app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(employee.bp)

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('employee.dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            current_user.full_name = request.form['full_name']
            current_user.email = request.form['email']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
            
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
