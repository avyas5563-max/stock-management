"""Sync Sales/Purchases with Money Transactions"""
import sys
sys.path.insert(0, 'c:\\Users\\Aditya\\Desktop\\stock_project')

from app import create_app, db
from app.models.sale import Sale
from app.models.purchase import Purchase
from app.models.money import Money

app = create_app()

with app.app_context():
    print("=" * 70)
    print("SYNCING SALES WITH MONEY TRANSACTIONS")
    print("=" * 70)
    
    sales_updated = 0
    sales_missing = 0
    
    # Check all sales
    sales = Sale.query.all()
    for sale in sales:
        money = Money.query.filter_by(reference_type='sale', reference_id=sale.sale_id).first()
        
        if money:
            # Update money record to match sale
            if (money.advance_payment != sale.advance_payment or 
                money.total_amount != sale.total_amount):
                
                print(f"\n[FIX] Fixing Sale #{sale.sale_id}")
                print(f"      Money: Rs{money.advance_payment:.2f} -> Rs{sale.advance_payment:.2f}")
                
                money.advance_payment = sale.advance_payment
                money.total_amount = sale.total_amount
                
                # Update status
                if sale.remaining_payment == 0:
                    money.pay_status = 'paid'
                elif sale.advance_payment > 0:
                    money.pay_status = 'partial'
                else:
                    money.pay_status = 'pending'
                
                sales_updated += 1
        else:
            print(f"[!!] Missing Money record for Sale #{sale.sale_id}")
            sales_missing += 1
    
    print("\n" + "=" * 70)
    print("SYNCING PURCHASES WITH MONEY TRANSACTIONS")
    print("=" * 70)
    
    purchases_updated = 0
    purchases_missing = 0
    
    # Check all purchases
    purchases = Purchase.query.all()
    for purchase in purchases:
        money = Money.query.filter_by(reference_type='purchase', reference_id=purchase.purchase_id).first()
        
        if money:
            # Update money record to match purchase
            if (money.advance_payment != purchase.advance_payment or 
                money.total_amount != purchase.total_amount):
                
                print(f"\n[FIX] Fixing Purchase #{purchase.purchase_id}")
                print(f"      Money: Rs{money.advance_payment:.2f} -> Rs{purchase.advance_payment:.2f}")
                
                money.advance_payment = purchase.advance_payment
                money.total_amount = purchase.total_amount
                
                # Update status
                if purchase.remaining_amount == 0:
                    money.pay_status = 'paid'
                elif purchase.advance_payment > 0:
                    money.pay_status = 'partial'
                else:
                    money.pay_status = 'pending'
                
                purchases_updated += 1
        else:
            print(f"[!!] Missing Money record for Purchase #{purchase.purchase_id}")
            purchases_missing += 1
    
    # Commit all changes
    db.session.commit()
    
    print("\n" + "=" * 70)
    print("SYNC COMPLETE")
    print("=" * 70)
    print(f"[OK] Sales synced: {sales_updated}")
    print(f"[!!] Sales missing money records: {sales_missing}")
    print(f"[OK] Purchases synced: {purchases_updated}")
    print(f"[!!] Purchases missing money records: {purchases_missing}")
    print("\n>>> Now refresh your Transactions page to see updated data!")
