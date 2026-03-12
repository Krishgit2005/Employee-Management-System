// Employee Management System Client Logic

class App {
    constructor() {
        this.employees = [];
        this.filteredEmployees = [];
        this.user = null; // Stores logged-in user details
        
        // Chart instances
        this.deptChart = null;
        this.statusChart = null;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        
        // Check for existing session
        const storedUser = localStorage.getItem('traction_user');
        if (storedUser) {
            this.user = JSON.parse(storedUser);
            this.showApp();
        }
    }

    setupEventListeners() {
        // Search
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal(e.target.id);
            }
        });

        // Sidebar Navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                // Remove active class from all
                navItems.forEach(nav => nav.classList.remove('active'));
                // Add to clicked
                item.classList.add('active');
                
                // Show corresponding view
                const targetViewId = 'view-' + item.dataset.view;
                const views = document.querySelectorAll('.view-section');
                views.forEach(view => view.classList.add('hidden'));
                document.getElementById(targetViewId).classList.remove('hidden');
            });
        });
    }

    // --- Authentication ---

    async handleLogin(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = document.getElementById('loginBtn');
        const loginData = Object.fromEntries(new FormData(form).entries());

        submitBtn.disabled = true;
        submitBtn.innerText = 'Authenticating...';

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(loginData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Login failed');
            }

            // Save user session
            this.user = result.user;
            localStorage.setItem('traction_user', JSON.stringify(this.user));
            
            this.showToast('Login successful', 'success');
            this.showApp();

        } catch (error) {
            this.showToast(error.message, 'error');
            console.error('Login error:', error);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerText = 'Sign in';
            form.reset();
        }
    }

    logout() {
        this.user = null;
        localStorage.removeItem('traction_user');
        document.getElementById('appContent').classList.add('hidden');
        document.getElementById('loginScreen').classList.remove('hidden');
    }

    async showApp() {
        // Toggle view
        document.getElementById('loginScreen').classList.add('hidden');
        document.getElementById('appContent').classList.remove('hidden');

        // Update UI based on Role
        this.applyRolePermissions();
        
        // Fetch data
        await this.fetchEmployees();
    }

    applyRolePermissions() {
        // Set User Profile in Sidebar
        document.getElementById('navUserName').innerText = this.user.username;
        document.getElementById('navUserRole').innerText = this.user.role;
        document.getElementById('navUserAvatar').innerText = this.user.username[0].toUpperCase();

        const isAdmin = this.user.role === 'admin';
        
        // Toggle Add Button
        const addBtn = document.getElementById('addEmployeeBtn');
        if (addBtn) addBtn.style.display = isAdmin ? 'inline-flex' : 'none';

        // Toggle Table Actions Column Header
        const actionHeaders = document.querySelectorAll('.admin-only-cell');
        actionHeaders.forEach(th => th.style.display = isAdmin ? 'table-cell' : 'none');
    }

    // --- API Calls ---

    async fetchEmployees() {
        try {
            const response = await fetch('/api/employees');
            if (!response.ok) throw new Error('Failed to fetch employees');
            
            this.employees = await response.json();
            this.filteredEmployees = [...this.employees];
            
            this.renderTable();
            this.renderStats();
            this.renderCharts(); // Add rendering charts here
        } catch (error) {
            console.error('Error fetching employees:', error);
            this.showToast('Failed to load employees', 'error');
            this.renderEmptyState('Failed to load data. Please try again.');
        }
    }

    async saveEmployee(employeeData, isEdit = false) {
        if (!this.user || this.user.role !== 'admin') {
            this.showToast('You do not have permission to do this.', 'error');
            return;
        }

        const method = isEdit ? 'PUT' : 'POST';
        const url = isEdit ? `/api/employees/${employeeData.id}` : '/api/employees';

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.user.token}`
                },
                body: JSON.stringify(employeeData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to save employee');
            }

            this.showToast(`Employee ${isEdit ? 'updated' : 'added'} successfully`, 'success');
            this.closeModal('employeeModal');
            await this.fetchEmployees(); // Refresh list

        } catch (error) {
            this.showToast(error.message, 'error');
            console.error('Save error:', error);
        }
    }

    async deleteEmployeeApi(id) {
        if (!this.user || this.user.role !== 'admin') return;

        try {
            const response = await fetch(`/api/employees/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.user.token}`
                }
            });

            if (!response.ok) {
                const result = await response.json();
                throw new Error(result.error || 'Failed to delete employee');
            }

            this.showToast('Employee deleted successfully', 'success');
            this.closeModal('deleteModal');
            await this.fetchEmployees();

        } catch (error) {
            this.showToast(error.message, 'error');
            console.error('Delete error:', error);
        }
    }


    // --- UI Rendering ---

    renderTable() {
        const tbody = document.getElementById('employeeTableBody');
        const isAdmin = this.user && this.user.role === 'admin';
        
        if (this.filteredEmployees.length === 0) {
            this.renderEmptyState('No employees found.');
            return;
        }

        tbody.innerHTML = this.filteredEmployees.map(emp => {
            // Get initials for avatar
            const initials = emp.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
            
            // Format status class
            const statusClass = emp.status.toLowerCase().replace(' ', '-');

            let actionCell = '';
            if (isAdmin) {
                actionCell = `
                    <td class="actions-cell">
                        <div class="actions-wrapper">
                            <button class="icon-btn edit" onclick="window.app.openEditModal(${emp.id})" title="Edit">
                                <i class="ph ph-pencil-simple"></i>
                            </button>
                            <button class="icon-btn delete" onclick="window.app.openDeleteModal(${emp.id}, '${this.escapeHTML(emp.name)}')" title="Delete">
                                <i class="ph ph-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
            }

            return `
                <tr>
                    <td>
                        <div class="emp-name-cell">
                            <div class="emp-avatar">${initials}</div>
                            <div class="emp-details">
                                <span class="emp-name">${this.escapeHTML(emp.name)}</span>
                                <span class="emp-email">${this.escapeHTML(emp.email)}</span>
                            </div>
                        </div>
                    </td>
                    <td>${this.escapeHTML(emp.role)}</td>
                    <td>${this.escapeHTML(emp.department)}</td>
                    <td>
                        <span class="status-badge ${statusClass}">
                            ${this.escapeHTML(emp.status)}
                        </span>
                    </td>
                    ${actionCell}
                </tr>
            `;
        }).join('');
    }

    renderEmptyState(message) {
        const tbody = document.getElementById('employeeTableBody');
        const isAdmin = this.user && this.user.role === 'admin';
        const colSpan = isAdmin ? '5' : '4';
        
        tbody.innerHTML = `
            <tr>
                <td colspan="${colSpan}" class="empty-state">
                    <i class="ph ph-users" style="font-size: 2rem; color: #cbd5e1; margin-bottom: 8px; display: block;"></i>
                    <p>${message}</p>
                </td>
            </tr>
        `;
    }

    renderStats() {
        const statsContainer = document.getElementById('statsContainer');
        
        const total = this.employees.length;
        const active = this.employees.filter(e => e.status === 'Active').length;
        
        // Count unique departments
        const departments = new Set(this.employees.map(e => e.department)).size;

        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-icon total">
                    <i class="ph ph-users-three"></i>
                </div>
                <div class="stat-info">
                    <h3>Total Employees</h3>
                    <div class="value">${total}</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon active">
                    <i class="ph ph-user-check"></i>
                </div>
                <div class="stat-info">
                    <h3>Active Staff</h3>
                    <div class="value">${active}</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon departments">
                    <i class="ph ph-buildings"></i>
                </div>
                <div class="stat-info">
                    <h3>Departments</h3>
                    <div class="value">${departments}</div>
                </div>
            </div>
        `;
    }

    renderCharts() {
        if (!window.Chart) return;
        
        // Aggregate Data
        const deptCounts = {};
        const statusCounts = {};

        this.employees.forEach(emp => {
            deptCounts[emp.department] = (deptCounts[emp.department] || 0) + 1;
            statusCounts[emp.status] = (statusCounts[emp.status] || 0) + 1;
        });

        // Common Chart Options
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { family: "'Outfit', sans-serif" },
                        padding: 20
                    }
                }
            }
        };

        // 1. Department Chart (Bar)
        const deptCtx = document.getElementById('departmentChart');
        if (deptCtx) {
            if (this.deptChart) this.deptChart.destroy();
            
            this.deptChart = new Chart(deptCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(deptCounts),
                    datasets: [{
                        label: 'Number of Employees',
                        data: Object.values(deptCounts),
                        backgroundColor: '#6366f1',
                        borderRadius: 6
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        y: { 
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

        // 2. Status Chart (Doughnut)
        const statusCtx = document.getElementById('statusChart');
        if (statusCtx) {
            if (this.statusChart) this.statusChart.destroy();
            
            // Match custom CSS colors
            const statusColors = {
                'Active': '#10b981',   // Green
                'Inactive': '#ef4444', // Red
                'On Leave': '#eab308'  // Yellow
            };

            const labels = Object.keys(statusCounts);
            const data = Object.values(statusCounts);
            const bgColors = labels.map(l => statusColors[l] || '#cbd5e1');

            this.statusChart = new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: bgColors,
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    ...commonOptions,
                    cutout: '70%'
                }
            });
        }
    }

    // --- Search & Filter ---

    handleSearch(query) {
        const searchTerm = query.toLowerCase().trim();
        
        if (!searchTerm) {
            this.filteredEmployees = [...this.employees];
        } else {
            this.filteredEmployees = this.employees.filter(emp => {
                return emp.name.toLowerCase().includes(searchTerm) || 
                       emp.email.toLowerCase().includes(searchTerm) ||
                       emp.role.toLowerCase().includes(searchTerm) ||
                       emp.department.toLowerCase().includes(searchTerm);
            });
        }
        
        this.renderTable();
    }


    // --- Modal Logic ---

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('open');
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('open');
        }
    }

    openAddModal() {
        document.getElementById('modalTitle').innerText = 'Add New Employee';
        document.getElementById('employeeForm').reset();
        document.getElementById('empId').value = '';
        this.openModal('employeeModal');
    }

    openEditModal(id) {
        const employee = this.employees.find(e => e.id === id);
        if (!employee) return;

        document.getElementById('modalTitle').innerText = 'Edit Employee';
        
        // Populate form
        document.getElementById('empId').value = employee.id;
        document.getElementById('empName').value = employee.name;
        document.getElementById('empEmail').value = employee.email;
        document.getElementById('empRole').value = employee.role;
        document.getElementById('empDepartment').value = employee.department;
        document.getElementById('empStatus').value = employee.status;

        this.openModal('employeeModal');
    }

    openDeleteModal(id, name) {
        document.getElementById('deleteEmpId').value = id;
        document.getElementById('deleteEmpName').innerText = name;
        this.openModal('deleteModal');
    }

    // --- Actions/Handlers ---

    handleFormSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = document.getElementById('saveEmployeeBtn');
        const originalText = submitBtn.innerText;
        
        submitBtn.disabled = true;
        submitBtn.innerText = 'Saving...';

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        const isEdit = data.id !== '';
        if (isEdit) {
            data.id = parseInt(data.id, 10);
        }

        this.saveEmployee(data, isEdit).finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerText = originalText;
        });
    }

    confirmDelete() {
        const id = document.getElementById('deleteEmpId').value;
        if (id) {
            this.deleteEmployeeApi(id);
        }
    }

    // --- Utilities ---

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const icon = type === 'success' ? 'check-circle' : 'warning-circle';
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="ph ph-${icon}" style="font-size: 1.5rem;"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    escapeHTML(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

// Initialize app when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Expose to window for inline event handlers
    window.app = new App();
});
