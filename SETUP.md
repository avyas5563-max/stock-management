# Quick Start Guide

## Installation Steps

1. **Install Python Dependencies**
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
   This creates: username=`admin`, password=`admin123`

5. **Run Application**
   ```bash
   python run.py
   ```

6. **Access Application**
   Open browser: http://localhost:5000

## Quick Commands

- **Initialize DB**: `flask initdb`
- **Create Admin**: `flask create_admin`
- **Run Server**: `python run.py`
- **Activate venv**: `venv\Scripts\activate`

## Default Login

- Username: `admin`
- Password: `admin123`

⚠️ Change password after first login!

## First Steps After Login

1. Go to **Categories** → Add product categories
2. Go to **Items** → Add your inventory items
3. Go to **Suppliers** → Add supplier information
4. Go to **Customers** → Add customer records
5. Start recording **Purchases** and **Sales**

## Features

✓ User Management (Admin/Manager/User roles)
✓ Inventory Tracking
✓ Purchase Management
✓ Sales Management
✓ Financial Tracking
✓ Low Stock Alerts
✓ Activity Logs
✓ Dashboard with Real-time Metrics

## Need Help?

Check README.md for detailed documentation.
