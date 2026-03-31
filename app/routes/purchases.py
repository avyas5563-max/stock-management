from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.purchase import Purchase, PurchaseItem
from app.models.supplier import Supplier
from app.models.item import Item
from app.models.inventory import Inventory
from app.models.money import Money
from app.utils.logger import log_action

purchases_bp = Blueprint('purchases', __name__)


@purchases_bp.route('/')
@login_required
def list_purchases():
    """List all purchases"""
    page = request.args.get('page', 1, type=int)
    purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('purchases/list.html', purchases=purchases)


@purchases_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_purchase():
    """Create new purchase"""
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        purchase_date = datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date()
        due_date = request.form.get('due_date')
        if due_date and due_date.strip():
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        else:
            due_date = None
        
        total_amount = float(request.form.get('total_amount', 0))
        advance_payment = float(request.form.get('advance_payment', 0))
        remaining_amount = total_amount - advance_payment
        
        purchase = Purchase(
            supplier_id=supplier_id,
            purchase_date=purchase_date,
            total_amount=total_amount,
            advance_payment=advance_payment,
            remaining_amount=remaining_amount,
            due_date=due_date,
            status='pending' if remaining_amount > 0 else 'completed',
            created_by=current_user.user_id
        )
        
        db.session.add(purchase)
        db.session.flush()
        
        # Add purchase items
        item_ids = request.form.getlist('item_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        for item_id, quantity, price in zip(item_ids, quantities, prices):
            if item_id and quantity and price:
                quantity = float(quantity)
                price = float(price)
                total = quantity * price
                
                purchase_item = PurchaseItem(
                    purchase_id=purchase.purchase_id,
                    item_id=int(item_id),
                    quantity=quantity,
                    price=price,
                    total=total,
                    created_by=current_user.user_id
                )
                db.session.add(purchase_item)
                
                # Update inventory
                inventory = Inventory.query.filter_by(item_id=int(item_id)).first()
                if inventory:
                    inventory.current_stock += quantity
                    inventory.updated_by = current_user.user_id
                else:
                    # Create inventory record if it doesn't exist
                    inventory = Inventory(
                        item_id=int(item_id),
                        current_stock=quantity,
                        created_by=current_user.user_id,
                        updated_by=current_user.user_id
                    )
                    db.session.add(inventory)
        
        db.session.flush()  # Ensure inventory is updated before committing
        # Update supplier balance
        supplier = Supplier.query.get(supplier_id)
        if supplier:
            supplier.current_balance += remaining_amount
        
        # Create money transaction
        money = Money(
            reference_type='purchase',
            reference_id=purchase.purchase_id,
            party_type='supplier',
            party_id=supplier_id,
            total_amount=total_amount,
            advance_payment=advance_payment,
            payment_type=request.form.get('payment_type', 'cash'),
            pay_status='paid' if remaining_amount == 0 else 'partial' if advance_payment > 0 else 'pending',
            due_date=due_date,
            created_by=current_user.user_id
        )
        db.session.add(money)
        
        db.session.commit()
        
        log_action(current_user.user_id, 'purchases', purchase.purchase_id, 'create', f'Created purchase for supplier ID: {supplier_id}')
        flash('Purchase created successfully!', 'success')
        return redirect(url_for('purchases.list_purchases'))
    
    suppliers = Supplier.query.all()
    items = Item.query.all()
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    return render_template('purchases/create.html', suppliers=suppliers, items=items, today=today)


@purchases_bp.route('/<int:purchase_id>/view')
@login_required
def view_purchase(purchase_id):
    """View purchase details"""
    purchase = Purchase.query.get_or_404(purchase_id)
    return render_template('purchases/view.html', purchase=purchase)


@purchases_bp.route('/<int:purchase_id>/update-payment', methods=['POST'])
@login_required
def update_payment(purchase_id):
    """Update payment for purchase"""
    purchase = Purchase.query.get_or_404(purchase_id)
    
    payment_amount = float(request.form.get('payment_amount', 0))
    new_due_date = request.form.get('due_date')
    
    if payment_amount < 0:
        flash('Payment amount cannot be negative!', 'danger')
        return redirect(url_for('purchases.view_purchase', purchase_id=purchase_id))
    
    if payment_amount > purchase.remaining_amount:
        flash(f'Payment amount cannot exceed remaining amount of ₹{purchase.remaining_amount:.2f}!', 'danger')
        return redirect(url_for('purchases.view_purchase', purchase_id=purchase_id))
    
    # Update purchase
    old_remaining = purchase.remaining_amount
    purchase.advance_payment += payment_amount
    purchase.remaining_amount -= payment_amount
    
    if purchase.remaining_amount == 0:
        purchase.status = 'completed'
    
    # Update due date if provided
    if new_due_date and new_due_date.strip():
        purchase.due_date = datetime.strptime(new_due_date, '%Y-%m-%d').date()
    
    purchase.updated_by = current_user.user_id
    
    # Update supplier balance
    supplier = Supplier.query.get(purchase.supplier_id)
    if supplier:
        supplier.current_balance -= payment_amount
    
    # Update money record
    money = Money.query.filter_by(reference_type='purchase', reference_id=purchase_id).first()
    if money:
        money.advance_payment = purchase.advance_payment
        money.pay_status = 'paid' if purchase.remaining_amount == 0 else 'partial' if purchase.advance_payment > 0 else 'pending'
        if new_due_date and new_due_date.strip():
            money.due_date = datetime.strptime(new_due_date, '%Y-%m-%d').date()
        money.updated_by = current_user.user_id
    
    db.session.commit()
    
    log_action(current_user.user_id, 'purchases', purchase_id, 'update', f'Payment updated: ₹{payment_amount:.2f}. Remaining: ₹{old_remaining:.2f} → ₹{purchase.remaining_amount:.2f}')
    flash(f'Payment of ₹{payment_amount:.2f} recorded successfully!', 'success')
    return redirect(url_for('purchases.view_purchase', purchase_id=purchase_id))


@purchases_bp.route('/<int:purchase_id>/delete', methods=['POST'])
@login_required
def delete_purchase(purchase_id):
    """Delete purchase"""
    purchase = Purchase.query.get_or_404(purchase_id)
    
    # Revert inventory changes
    for purchase_item in purchase.items:
        inventory = Inventory.query.filter_by(item_id=purchase_item.item_id).first()
        if inventory:
            inventory.current_stock -= purchase_item.quantity
    
    # Update supplier balance
    supplier = Supplier.query.get(purchase.supplier_id)
    supplier.current_balance -= purchase.remaining_amount
    
    log_action(current_user.user_id, 'purchases', purchase.purchase_id, 'delete', f'Deleted purchase ID: {purchase_id}')
    
    db.session.delete(purchase)
    db.session.commit()
    
    flash('Purchase deleted successfully!', 'success')
    return redirect(url_for('purchases.list_purchases'))
