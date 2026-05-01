"""Fix payment mismatches in correct way"""
import sys
sys.path.insert(0, 'c:\\Users\\Aditya\\Desktop\\stock_project')

from app import create_app, db
from app.models.sale import Sale
from app.models.purchase import Purchase
from app.models.customer import Customer
from app.models.supplier import Supplier

app = create_app()

with app.app_context():
    print("=" * 70)
    print("CHECKING FOR PAYMENT MISMATCHES")
    print("=" * 70)
    
    # Check Sales vs Customer Balances
    # check krio hona chaiye ye change commit 
    print("\n📊 SALES STATUS:")
    sales = Sale.query.all()
    for sale in sales:
        customer = Customer.query.get(sale.customer_id)
        print(f"\nSale ID {sale.sale_id} - Customer: {customer.name}")
        print(f"  Sale Remaining: ₹{sale.remaining_payment:.2f}")
        print(f"  Customer Balance: ₹{customer.current_balance:.2f}")
        print(f"  Status: {sale.status}")
        
        if sale.remaining_payment > 0 and customer.current_balance == 0:
            print(f"  ⚠️ MISMATCH! Sale shows pending but customer balance is 0")
    
    # Check Purchases vs Supplier Balances  
    print("\n📊 PURCHASES STATUS:")
    purchases = Purchase.query.all()
    for purchase in purchases:
        supplier = Supplier.query.get(purchase.supplier_id)
        print(f"\nPurchase ID {purchase.purchase_id} - Supplier: {supplier.supplier_name}")
        print(f"  Purchase Remaining: ₹{purchase.remaining_amount:.2f}")
        print(f"  Supplier Balance: ₹{supplier.current_balance:.2f}")
        print(f"  Status: {purchase.status}")
        
        if purchase.remaining_amount > 0 and supplier.current_balance == 0:
            print(f"  ⚠️ MISMATCH! Purchase shows pending but supplier balance is 0")
    
    print("\n" + "=" * 70)
    print("FIX OPTIONS:")
    print("=" * 70)
    print("1. Clear all sale/purchase remaining amounts (mark as completed)")
    print("2. Keep as is (manual investigation needed)")
    print()
    
    choice = input("Enter 1 to fix, or 2 to cancel: ")
    
    if choice == '1':
        print("\n🔧 FIXING MISMATCHES...")
        fixed_sales = 0
        fixed_purchases = 0
        
        # Fix sales where customer balance is 0 but sale shows remaining
        for sale in sales:
            customer = Customer.query.get(sale.customer_id)
            if sale.remaining_payment > 0 and customer.current_balance == 0:
                print(f"✓ Fixing Sale ID {sale.sale_id}: Setting remaining to 0, status to completed")
                sale.advance_payment = sale.total_amount
                sale.remaining_payment = 0
                sale.status = 'completed'
                fixed_sales += 1
        
        # Fix purchases where supplier balance is 0 but purchase shows remaining
        for purchase in purchases:
            supplier = Supplier.query.get(purchase.supplier_id)
            if purchase.remaining_amount > 0 and supplier.current_balance == 0:
                print(f"✓ Fixing Purchase ID {purchase.purchase_id}: Setting remaining to 0, status to completed")
                purchase.advance_payment = purchase.total_amount
                purchase.remaining_amount = 0
                purchase.status = 'completed'
                fixed_purchases += 1
        
        db.session.commit()
        
        print(f"\n✅ FIXED: {fixed_sales} sales and {fixed_purchases} purchases")
        print("Now refresh your dashboard to see updated amounts!")
    else:
        print("\n❌ No changes made.")
