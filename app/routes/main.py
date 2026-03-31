from flask import Blueprint, render_template, make_response, jsonify
from flask_login import login_required, current_user
from app.models.item import Item
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.inventory import Inventory
from sqlalchemy import func
from app import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Expire session to get fresh data from database
    db.session.expire_all()
    
    # Get statistics
    total_items = Item.query.count()
    total_customers = Customer.query.count()
    total_suppliers = Supplier.query.count()
    
    # Recent purchases and sales
    recent_purchases = Purchase.query.order_by(Purchase.created_at.desc()).limit(5).all()
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    
    # Low stock items
    low_stock_items = db.session.query(Item, Inventory).join(
        Inventory, Item.item_id == Inventory.item_id
    ).filter(
        Inventory.current_stock < Item.min_stock
    ).limit(10).all()
    
    # Total sales and purchases this month
    from datetime import datetime, timedelta
    first_day = datetime.now().replace(day=1)
    
    total_sales = db.session.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= first_day
    ).scalar() or 0
    
    total_purchases = db.session.query(func.sum(Purchase.total_amount)).filter(
        Purchase.purchase_date >= first_day
    ).scalar() or 0
    
    # Financial Summary - Pending amounts
    # Only sum where remaining payment/amount is greater than 0 and status is not cancelled
    total_receivables = db.session.query(func.sum(Sale.remaining_payment)).filter(
        Sale.remaining_payment > 0,
        Sale.status != 'cancelled'
    ).scalar() or 0  # Customers owe us
    
    total_payables = db.session.query(func.sum(Purchase.remaining_amount)).filter(
        Purchase.remaining_amount > 0,
        Purchase.status != 'cancelled'
    ).scalar() or 0  # We owe suppliers
    
    # Pending sales and purchases count (only those with remaining amounts > 0)
    pending_sales = Sale.query.filter(
        Sale.remaining_payment > 0,
        Sale.status != 'cancelled'
    ).count()
    
    pending_purchases = Purchase.query.filter(
        Purchase.remaining_amount > 0,
        Purchase.status != 'cancelled'
    ).count()
    
    # Daily Sales & Purchases (Last 7 Days)
    daily_labels = []
    daily_sales_data = []
    daily_purchases_data = []
    
    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        daily_labels.append(day.strftime('%b %d'))
        
        day_sales = db.session.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date >= day_start,
            Sale.sale_date <= day_end
        ).scalar() or 0
        
        day_purchases = db.session.query(func.sum(Purchase.total_amount)).filter(
            Purchase.purchase_date >= day_start,
            Purchase.purchase_date <= day_end
        ).scalar() or 0
        
        daily_sales_data.append(float(day_sales))
        daily_purchases_data.append(float(day_purchases))
    
    # Monthly Sales & Purchases (Last 6 Months)
    monthly_labels = []
    monthly_sales_data = []
    monthly_purchases_data = []
    
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate next month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1)
        
        monthly_labels.append(month_start.strftime('%b %Y'))
        
        month_sales = db.session.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date < month_end
        ).scalar() or 0
        
        month_purchases = db.session.query(func.sum(Purchase.total_amount)).filter(
            Purchase.purchase_date >= month_start,
            Purchase.purchase_date < month_end
        ).scalar() or 0
        
        monthly_sales_data.append(float(month_sales))
        monthly_purchases_data.append(float(month_purchases))
    
    # Calculate percentage change (current month vs previous month)
    prev_month_sales = monthly_sales_data[-2] if len(monthly_sales_data) > 1 else 0
    curr_month_sales = monthly_sales_data[-1] if monthly_sales_data else 0
    
    if prev_month_sales > 0:
        sales_change_percent = ((curr_month_sales - prev_month_sales) / prev_month_sales) * 100
    else:
        sales_change_percent = 100 if curr_month_sales > 0 else 0
    
    prev_month_purchases = monthly_purchases_data[-2] if len(monthly_purchases_data) > 1 else 0
    curr_month_purchases = monthly_purchases_data[-1] if monthly_purchases_data else 0
    
    if prev_month_purchases > 0:
        purchases_change_percent = ((curr_month_purchases - prev_month_purchases) / prev_month_purchases) * 100
    else:
        purchases_change_percent = 100 if curr_month_purchases > 0 else 0
    
    # Render template
    response = make_response(render_template('main/dashboard.html',
                         total_items=total_items,
                         total_customers=total_customers,
                         total_suppliers=total_suppliers,
                         recent_purchases=recent_purchases,
                         recent_sales=recent_sales,
                         low_stock_items=low_stock_items,
                         total_sales=total_sales,
                         total_purchases=total_purchases,
                         total_receivables=total_receivables,
                         total_payables=total_payables,
                         pending_sales=pending_sales,
                         pending_purchases=pending_purchases,
                         daily_labels=daily_labels,
                         daily_sales_data=daily_sales_data,
                         daily_purchases_data=daily_purchases_data,
                         monthly_labels=monthly_labels,
                         monthly_sales_data=monthly_sales_data,
                         monthly_purchases_data=monthly_purchases_data,
                         sales_change_percent=sales_change_percent,
                         purchases_change_percent=purchases_change_percent))
    
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


@main_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats():
    """API endpoint for real-time dashboard statistics"""
    from datetime import datetime, timedelta
    
    # Expire session to get fresh data
    db.session.expire_all()
    
    # Financial Summary - Pending amounts
    total_receivables = db.session.query(func.sum(Sale.remaining_payment)).filter(
        Sale.remaining_payment > 0,
        Sale.status != 'cancelled'
    ).scalar() or 0
    
    total_payables = db.session.query(func.sum(Purchase.remaining_amount)).filter(
        Purchase.remaining_amount > 0,
        Purchase.status != 'cancelled'
    ).scalar() or 0
    
    # Pending counts
    pending_sales = Sale.query.filter(
        Sale.remaining_payment > 0,
        Sale.status != 'cancelled'
    ).count()
    
    pending_purchases = Purchase.query.filter(
        Purchase.remaining_amount > 0,
        Purchase.status != 'cancelled'
    ).count()
    
    # Total sales and purchases this month
    first_day = datetime.now().replace(day=1)
    
    total_sales = db.session.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= first_day
    ).scalar() or 0
    
    total_purchases = db.session.query(func.sum(Purchase.total_amount)).filter(
        Purchase.purchase_date >= first_day
    ).scalar() or 0
    
    # Low stock count
    low_stock_count = db.session.query(Item, Inventory).join(
        Inventory, Item.item_id == Inventory.item_id
    ).filter(
        Inventory.current_stock < Item.min_stock
    ).count()
    
    return jsonify({
        'success': True,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data': {
            'total_receivables': float(total_receivables),
            'total_payables': float(total_payables),
            'pending_sales': pending_sales,
            'pending_purchases': pending_purchases,
            'total_sales': float(total_sales),
            'total_purchases': float(total_purchases),
            'low_stock_count': low_stock_count,
            'total_items': Item.query.count(),
            'total_customers': Customer.query.count(),
            'total_suppliers': Supplier.query.count()
        }
    })


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')
