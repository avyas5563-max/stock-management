# 🚀 Stock Management System - Complete Setup Guide

## 📋 Project Overview

A comprehensive Flask-based inventory management system with:
- ✅ 12 interconnected database tables
- ✅ User authentication & authorization (Admin/Manager/User roles)
- ✅ Complete CRUD operations for all modules
- ✅ Real-time dashboard with business metrics
- ✅ Purchase & sales management with inventory tracking
- ✅ Financial transaction monitoring
- ✅ Activity logging & audit trail
- ✅ Low stock alerts
- ✅ Clean, modular architecture

## 🏗️ Project Structure

```
stock_project/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models/                  # Database models (12 tables)
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── item.py
│   │   ├── supplier.py
│   │   ├── customer.py
│   │   ├── purchase.py
│   │   ├── sale.py
│   │   ├── inventory.py
│   │   ├── money.py
│   │   └── log.py
│   ├── routes/                  # Blueprint routes (12 modules)
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── users.py
│   │   ├── categories.py
│   │   ├── items.py
│   │   ├── suppliers.py
│   │   ├── customers.py
│   │   ├── purchases.py
│   │   ├── sales.py
│   │   ├── inventory.py
│   │   ├── money.py
│   │   └── logs.py
│   ├── templates/               # HTML templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── main/
│   │   ├── users/
│   │   ├── categories/
│   │   ├── items/
│   │   ├── suppliers/
│   │   ├── customers/
│   │   ├── purchases/
│   │   ├── sales/
│   │   ├── inventory/
│   │   ├── money/
│   │   └── logs/
│   ├── static/                  # Static files
│   │   └── css/
│   └── utils/                   # Utility functions
│       ├── decorators.py
│       ├── logger.py
│       └── filters.py
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── requirements.txt             # Dependencies
├── setup.bat                    # Auto-setup script
├── start.bat                    # Quick start script
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore file
├── README.md                    # Full documentation
└── SETUP.md                     # Quick setup guide
```

## ⚡ Quick Start (2 Minutes)

### Option 1: Automated Setup (Windows)
```bash
# Simply run the setup script:
setup.bat

# Then start the application:
start.bat
```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Environment**
   ```bash
   copy .env.example .env
   ```

3. **Initialize Database**
   ```bash
   flask initdb
   ```

4. **Create Admin User**
   ```bash
   flask create_admin
   ```
   - Username: `admin`
   - Password: `admin123`

5. **Run Application**
   ```bash
   python run.py
   ```

6. **Access Application**
   - Open browser: http://localhost:5000
   - Login with admin credentials

## 🗄️ Database Schema (12 Tables)

### 1. **Users Table**
- user_id (PK)
- name, username, password
- role (admin/manager/user)
- status (active/inactive)
- created_by, updated_by, timestamps

### 2. **Categories Table**
- category_id (PK)
- name
- audit fields

### 3. **Items Table**
- item_id (PK)
- item_name, category_id (FK)
- unit, purchase_price, sale_price, min_stock
- audit fields

### 4. **Suppliers Table**
- supplier_id (PK)
- supplier_name, phone, address
- current_balance
- audit fields

### 5. **Customers Table**
- customer_id (PK)
- name, phone, address
- current_balance
- audit fields

### 6. **Purchases Table**
- purchase_id (PK)
- supplier_id (FK), purchase_date
- total_amount, advance_payment, remaining_amount
- due_date, status
- audit fields

### 7. **Purchase Items Table**
- id (PK)
- purchase_id (FK), item_id (FK)
- quantity, price, total
- audit fields

### 8. **Sales Table**
- sale_id (PK)
- customer_id (FK), sale_date
- total_amount, advance_payment, remaining_payment
- due_date, status
- audit fields

### 9. **Sale Items Table**
- id (PK)
- sale_id (FK), item_id (FK)
- quantity, price, total
- audit fields

### 10. **Inventory Table**
- item_id (PK, FK)
- current_stock, last_updated
- audit fields

### 11. **Money Table**
- transaction_id (PK)
- reference_type, reference_id
- party_type, party_id
- total_amount, advance_payment
- payment_type, pay_status
- due_date, reminder_date
- audit fields

### 12. **Logs Table**
- log_id (PK)
- user_id (FK)
- table_name, record_id
- action_taken, description
- action_date, last_updated

## 🎯 Features by Module

### Authentication & User Management
- Login/Logout with session management
- Role-based access control (RBAC)
- User CRUD operations
- Password hashing with Werkzeug

### Inventory Management
- Add/Edit/Delete items
- Category management
- Real-time stock tracking
- Low stock alerts
- Stock history

### Purchase Management
- Create multi-item purchases
- Supplier management
- Payment tracking
- Automatic inventory updates
- Purchase history

### Sales Management
- Create multi-item sales
- Customer management
- Payment tracking
- Automatic inventory deduction
- Sales history

### Financial Tracking
- Transaction management
- Payment status tracking
- Due date reminders
- Party balance management
- Payment type tracking

### Reporting & Logs
- Dashboard with real-time metrics
- Activity audit trail
- Low stock alerts
- Recent transactions view
- Filterable logs

## 🔧 Configuration

### Environment Variables (.env)
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///stock_management.db
FLASK_APP=run.py
FLASK_ENV=development
```

### Database
- Development: SQLite (default)
- Production: PostgreSQL/MySQL (configure in .env)

## 📱 User Workflows

### First Time Setup
1. Login as admin
2. Create categories (e.g., Electronics, Food, Clothing)
3. Add items with pricing and stock info
4. Add suppliers and customers
5. Start recording transactions

### Daily Operations

**Recording a Purchase:**
1. Navigate to Purchases → New Purchase
2. Select supplier
3. Add items with quantities
4. Set payment details
5. Submit (inventory auto-updates)

**Making a Sale:**
1. Navigate to Sales → New Sale
2. Select customer
3. Add items (stock auto-deducted)
4. Set payment details
5. Complete transaction

**Monitoring Inventory:**
1. Check Dashboard for low stock alerts
2. Navigate to Inventory
3. View current stock levels
4. Filter by status (Low/Out of Stock)

**Tracking Finances:**
1. Navigate to Transactions
2. Filter by status (Pending/Partial/Paid)
3. Update payments as needed
4. Monitor due dates

## 🔒 Security Features

- Password hashing (Werkzeug)
- Session management (Flask-Login)
- Role-based access control
- Input validation
- SQL injection protection (SQLAlchemy ORM)
- CSRF protection (Flask-WTF)

## 🚀 Deployment

### Production Checklist
- [ ] Change SECRET_KEY in .env
- [ ] Use PostgreSQL/MySQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set FLASK_ENV=production
- [ ] Configure proper logging
- [ ] Setup automatic backups
- [ ] Use Gunicorn/uWSGI
- [ ] Setup reverse proxy (Nginx)

### Example Production Config
```python
# In config.py
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Add more production settings
```

## 🛠️ Customization

### Adding New Features
1. Create model in `app/models/`
2. Create routes in `app/routes/`
3. Create templates in `app/templates/`
4. Register blueprint in `app/__init__.py`

### Modifying Design
- Edit `app/templates/base.html` for layout
- Add CSS in `app/static/css/`
- Modify Bootstrap classes in templates

## 📞 Support & Troubleshooting

### Common Issues

**Database not found:**
```bash
flask initdb
```

**Import errors:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
Change port in `run.py`:
```python
app.run(port=5001)
```

**Login issues:**
Recreate admin user:
```bash
flask create_admin
```

## 📊 Technologies Used

- **Backend:** Flask 3.0.0
- **Database:** SQLAlchemy 2.0.23
- **Authentication:** Flask-Login 0.6.3
- **Forms:** Flask-WTF 1.2.1
- **Frontend:** Bootstrap 5.3.0, jQuery
- **Icons:** Bootstrap Icons 1.11.0

## 📄 License

This project is provided as-is for educational and commercial use.

## ✨ Credits

Built with Flask framework using best practices:
- Application Factory Pattern
- Blueprint Architecture
- ORM with SQLAlchemy
- Template Inheritance
- Modular Design
- RESTful Routing

---

**Made with ❤️ for efficient stock management**

For more details, see README.md
