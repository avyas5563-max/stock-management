# Stock Management System

A comprehensive Flask-based inventory and stock management system with sales, purchases, and financial tracking.

## Features

- **User Management**: Role-based access control (Admin, Manager, User)
- **Inventory Management**: Track items, categories, and stock levels
- **Purchase Management**: Record and manage supplier purchases
- **Sales Management**: Handle customer sales transactions
- **Financial Tracking**: Monitor payments, balances, and transactions
- **Activity Logs**: Comprehensive audit trail of all actions
- **Dashboard**: Real-time overview of business metrics
- **Low Stock Alerts**: Automatic notifications for items below minimum stock

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or extract the project**
   ```bash
   cd stock_project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update the values in `.env` as needed
   ```bash
   copy .env.example .env
   ```

6. **Initialize the database**
   ```bash
   flask initdb
   ```

7. **Create an admin user**
   ```bash
   flask create_admin
   ```
   Default credentials: username=`admin`, password=`admin123`

8. **Run the application**
   ```bash
   python run.py
   ```

9. **Access the application**
   Open your browser and navigate to: `http://localhost:5000`

## Project Structure

```
stock_project/
├── app/
│   ├── __init__.py           # Application factory
│   ├── models/               # Database models
│   │   ├── user.py
│   │   ├── item.py
│   │   ├── category.py
│   │   ├── supplier.py
│   │   ├── customer.py
│   │   ├── purchase.py
│   │   ├── sale.py
│   │   ├── inventory.py
│   │   ├── money.py
│   │   └── log.py
│   ├── routes/               # Blueprint routes
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── users.py
│   │   ├── items.py
│   │   ├── categories.py
│   │   ├── suppliers.py
│   │   ├── customers.py
│   │   ├── purchases.py
│   │   ├── sales.py
│   │   ├── inventory.py
│   │   ├── money.py
│   │   └── logs.py
│   ├── templates/            # HTML templates
│   ├── static/               # Static files (CSS, JS, images)
│   └── utils/                # Utility functions
│       ├── decorators.py
│       ├── logger.py
│       └── filters.py
├── config.py                 # Configuration
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Database Schema

The application uses 12 interconnected tables:

1. **Users** - User accounts and authentication
2. **Categories** - Item categorization
3. **Items** - Product/inventory items
4. **Suppliers** - Vendor information
5. **Customers** - Customer records
6. **Purchases** - Purchase orders
7. **Purchase Items** - Individual items in purchases
8. **Sales** - Sales transactions
9. **Sale Items** - Individual items in sales
10. **Inventory** - Current stock levels
11. **Money** - Financial transactions
12. **Logs** - Activity audit trail

## Usage

### First Time Setup

1. Log in with admin credentials
2. Create categories for your items
3. Add items with pricing and stock information
4. Add suppliers and customers
5. Start recording purchases and sales

### Daily Operations

- **Record Purchases**: Navigate to Purchases → Create New Purchase
- **Make Sales**: Navigate to Sales → Create New Sale
- **Check Inventory**: View current stock levels and low stock alerts
- **Track Payments**: Monitor outstanding payments and balances
- **View Reports**: Dashboard provides real-time business metrics

## Default Admin Credentials

- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the admin password immediately after first login!

## Security Notes

- Change the `SECRET_KEY` in `.env` before deploying to production
- Use a proper database (PostgreSQL/MySQL) instead of SQLite for production
- Enable HTTPS in production environments
- Regularly backup your database
- Review and update user permissions regularly

## Development

To run in development mode with debug enabled:

```bash
set FLASK_ENV=development
python run.py
```

## Troubleshooting

### Database Issues
If you encounter database errors, try:
```bash
flask initdb
```

### Import Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Port Already in Use
Change the port in `run.py` or kill the process using port 5000

## Contributing

This is a modular Flask application. To add new features:

1. Create new models in `app/models/`
2. Create routes in `app/routes/`
3. Add templates in `app/templates/`
4. Register blueprints in `app/__init__.py`

## License

This project is provided as-is for educational and commercial use.

## Support

For issues and questions, please refer to the inline documentation in the code.
