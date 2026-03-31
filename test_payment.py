"""Test payment completion"""
import sys
sys.path.insert(0, 'c:\\Users\\Aditya\\Desktop\\stock_project')

from app import create_app, db
from app.models.sale import Sale
from app.models.purchase import Purchase

app = create_app()

with app.app_context():
    print("\nWhich transaction do you want to complete?")
    print("1. Sale ID 1 (Remaining: ₹26,000)")
    print("2. Purchase ID 1 (Remaining: ₹66,000)")
    
    choice = input("\nEnter 1 or 2: ")
    
    if choice == '1':
        sale = Sale.query.get(1)
        print(f"\nBEFORE: Status={sale.status}, Remaining=₹{sale.remaining_payment:.2f}")
        
        # Complete the payment
        sale.advance_payment += sale.remaining_payment
        sale.remaining_payment = 0
        sale.status = 'completed'
        db.session.commit()
        
        print(f"AFTER: Status={sale.status}, Remaining=₹{sale.remaining_payment:.2f}")
        print("\n✓ Sale ID 1 completed! Now refresh dashboard.")
        
    elif choice == '2':
        purchase = Purchase.query.get(1)
        print(f"\nBEFORE: Status={purchase.status}, Remaining=₹{purchase.remaining_amount:.2f}")
        
        # Complete the payment
        purchase.advance_payment += purchase.remaining_amount
        purchase.remaining_amount = 0
        purchase.status = 'completed'
        db.session.commit()
        
        print(f"AFTER: Status={purchase.status}, Remaining=₹{purchase.remaining_amount:.2f}")
        print("\n✓ Purchase ID 1 completed! Now refresh dashboard.")
