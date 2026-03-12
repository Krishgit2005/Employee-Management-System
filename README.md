# Premium Employee Management System (EMS)

A sophisticated, modern Employee Management System built with Flask, featuring a high-end **Glassmorphism** design system and robust administrative functionalities.

![EMS Preview](https://img.shields.io/badge/UI-Premium_Glassmorphism-6366f1)
![Flask](https://img.shields.io/badge/Framework-Flask-black)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)

## ✨ Key Features

### 🎨 Premium UI/UX
- **Glassmorphism Aesthetics**: Modern backdrop blurs, subtle glowing borders, and vibrant gradients.
- **Outfit Typography**: Clean, professional typography for a premium look and feel.
- **Phosphor Icons**: Elegant and consistent iconography across the platform.
- **Responsive Design**: Fluid layouts that adapt to various screen sizes.

### 🛠️ Admin Capabilities
- **Real-time Dashboard**: Overview of key metrics (Employee count, pending leaves, today's attendance).
- **Employee Management**: Full CRUD operations for managing the workforce.
- **Daily Attendance Roster**: Monitor live attendance status for all team members.
- **Payroll Processing**: Process monthly salaries with automated deduction handling and duplicate prevention.
- **Leave Control Center**: Review, approve, or reject employee leave requests.

### 👥 Employee Self-Service
- **Personal Dashboard**: High-level overview of attendance and salary history.
- **Attendance Management**: Mark daily attendance with a single click.
- **Leave Applications**: Streamlined form for submitting and tracking time-off requests.
- **Digital Payslips**: Access detailed, print-friendly monthly salary slips.
- **Profile Portal**: Manage personal contact information and account details.

## 🚀 Tech Stack

- **Backend**: Python, Flask
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System)
- **Icons**: Phosphor Icons Library
- **Typography**: Google Fonts (Outfit)

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Krishgit2005/Employee-Management-System.git
   cd Employee-Management-System
   ```

2. **Set up a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the portal**:
   Open your browser and navigate to `http://127.0.0.1:5000`

## 🔑 Default Credentials

- **Admin Account**:
  - Username: `admin`
  - Password: `admin123`

- **Test Employee**:
  - Username: `krish`
  - Password: `krish123`

---

## 🏗️ Project Structure
```text
├── app.py              # Application entry point
├── models.py           # SQLAlchemy database models
├── routes/             # Blueprint-based route definitions
│   ├── admin.py        # Admin-specific workflows
│   ├── employee.py     # Employee-specific workflows
│   └── auth.py         # Authentication logic
├── templates/          # HTML templates (Jinja2)
├── static/             
│   ├── css/            # Custom Premium Design System
│   └── js/             # Frontend logic
└── requirements.txt    # Project dependencies
```

## 📜 License
This project is for educational purposes and showcases modern web engineering practices.
