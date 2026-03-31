"""Check database state for debugging"""
import sys
sys.path.insert(0, 'c:\\Users\\Aditya\\Desktop\\stock_project')

from app import create_app, db
from app.models.sale import Sale
from app.models.purchase import Purchase

app = create_app()

with app.app_context():
    print("=" * 60)
    print("SALES - All Records")
    print("=" * 60)
    sales = Sale.query.all()
    for sale in sales:
        print(f"Sale ID: {sale.sale_id}, Status: {sale.status}")
        print(f"  Total: ₹{sale.total_amount:.2f}")
        print(f"  Advance: ₹{sale.advance_payment:.2f}")
        print(f"  Remaining: ₹{sale.remaining_payment:.2f}")
        print()
    
    print("=" * 60)
    print("PURCHASES - All Records")
    print("=" * 60)
    purchases = Purchase.query.all()
    for purchase in purchases:
        print(f"Purchase ID: {purchase.purchase_id}, Status: {purchase.status}")
        print(f"  Total: ₹{purchase.total_amount:.2f}")
        print(f"  Advance: ₹{purchase.advance_payment:.2f}")
        print(f"  Remaining: ₹{purchase.remaining_amount:.2f}")
        print()
    
    print("=" * 60)
    print("DASHBOARD CALCULATIONS")
    print("=" * 60)
    
    from sqlalchemy import func
    
    # Current query logic
    total_receivables = db.session.query(func.sum(Sale.remaining_payment)).filter(
        Sale.remaining_payment > 0,
        Sale.status != 'cancelled'
    ).scalar() or 0
    
    total_payables = db.session.query(func.sum(Purchase.remaining_amount)).filter(
        Purchase.remaining_amount > 0,
        Purchase.status != 'cancelled'
    ).scalar() or 0
    
    pending_sales = Sale.query.filter(
        Sale.remaining_payment > 0,
        Sale.status != 'cancelled'
    ).count()
    
    pending_purchases = Purchase.query.filter(
        Purchase.remaining_amount > 0,
        Purchase.status != 'cancelled'
    ).count()
    
    print(f"Total Receivables: ₹{total_receivables:.2f}")
    print(f"Total Payables: ₹{total_payables:.2f}")
    print(f"Pending Sales Count: {pending_sales}")
    print(f"Pending Purchases Count: {pending_purchases}")
    print()
    
    # Show which ones are included
    print("Sales with remaining > 0:")
    pending_sales_list = Sale.query.filter(
        Sale.remaining_payment > 0,
        Sale.status != 'cancelled'
    ).all()
    for sale in pending_sales_list:
        print(f"  ID {sale.sale_id}: ₹{sale.remaining_payment:.2f} remaining")
    
    print("\nPurchases with remaining > 0:")
    pending_purchases_list = Purchase.query.filter(
        Purchase.remaining_amount > 0,
        Purchase.status != 'cancelled'
    ).all()
    for purchase in pending_purchases_list:
        print(f"  ID {purchase.purchase_id}: ₹{purchase.remaining_amount:.2f} remaining")
