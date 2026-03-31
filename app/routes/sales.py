from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.sale import Sale, SaleItem
from app.models.customer import Customer
from app.models.item import Item
from app.models.inventory import Inventory
from app.models.money import Money
from app.utils.logger import log_action

sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/')
@login_required
def list_sales():
    """List all sales"""
    page = request.args.get('page', 1, type=int)
    sales = Sale.query.order_by(Sale.sale_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('sales/list.html', sales=sales)


@sales_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_sale():
    """Create new sale"""
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        sale_date = datetime.strptime(request.form.get('sale_date'), '%Y-%m-%d').date()
        due_date = request.form.get('due_date')
        if due_date and due_date.strip():
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        else:
            due_date = None
        
        total_amount = float(request.form.get('total_amount', 0))
        advance_payment = float(request.form.get('advance_payment', 0))
        remaining_payment = total_amount - advance_payment
        
        sale = Sale(
            customer_id=customer_id,
            sale_date=sale_date,
            total_amount=total_amount,
            advance_payment=advance_payment,
            remaining_payment=remaining_payment,
            due_date=due_date,
            status='pending' if remaining_payment > 0 else 'completed',
            created_by=current_user.user_id
        )
        
        db.session.add(sale)
        db.session.flush()
        
        # Add sale items
        item_ids = request.form.getlist('item_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        # First, validate all items have sufficient stock
        for item_id, quantity in zip(item_ids, quantities):
            if item_id and quantity:
                quantity = float(quantity)
                item = Item.query.get(int(item_id))
                inventory = Inventory.query.filter_by(item_id=int(item_id)).first()
                
                if not inventory:
                    db.session.rollback()
                    flash(f'Error: {item.item_name} has no inventory record. Please add stock first!', 'danger')
                    customers = Customer.query.all()
                    items = Item.query.all()
                    from datetime import date
                    today = date.today().strftime('%Y-%m-%d')
                    return render_template('sales/create.html', customers=customers, items=items, today=today)
                
                if inventory.current_stock < quantity:
                    db.session.rollback()
                    available = int(round(inventory.current_stock)) if inventory.current_stock == int(inventory.current_stock) else inventory.current_stock
                    requested = int(round(quantity)) if quantity == int(quantity) else quantity
                    flash(f'Error: Insufficient stock for {item.item_name}! Available: {available} {item.unit}, Requested: {requested} {item.unit}', 'danger')
                    customers = Customer.query.all()
                    items = Item.query.all()
                    from datetime import date
                    today = date.today().strftime('%Y-%m-%d')
                    return render_template('sales/create.html', customers=customers, items=items, today=today)
        
        # All validations passed, now create sale items and update inventory
        for item_id, quantity, price in zip(item_ids, quantities, prices):
            if item_id and quantity and price:
                quantity = float(quantity)
                price = float(price)
                total = quantity * price
                
                sale_item = SaleItem(
                    sale_id=sale.sale_id,
                    item_id=int(item_id),
                    quantity=quantity,
                    price=price,
                    total=total,
                    created_by=current_user.user_id
                )
                db.session.add(sale_item)
                
                # Update inventory (decrease stock)
                inventory = Inventory.query.filter_by(item_id=int(item_id)).first()
                inventory.current_stock -= quantity
                inventory.updated_by = current_user.user_id
        
        # Update customer balance
        customer = Customer.query.get(customer_id)
        if customer:
            customer.current_balance += remaining_payment
        
        # Create money transaction
        money = Money(
            reference_type='sale',
            reference_id=sale.sale_id,
            party_type='customer',
            party_id=customer_id,
            total_amount=total_amount,
            advance_payment=advance_payment,
            payment_type=request.form.get('payment_type', 'cash'),
            pay_status='paid' if remaining_payment == 0 else 'partial' if advance_payment > 0 else 'pending',
            due_date=due_date,
            created_by=current_user.user_id
        )
        db.session.add(money)
        
        db.session.commit()
        
        log_action(current_user.user_id, 'sales', sale.sale_id, 'create', f'Created sale for customer ID: {customer_id}')
        flash('Sale created successfully!', 'success')
        return redirect(url_for('sales.list_sales'))
    
    customers = Customer.query.all()
    items = Item.query.all()
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    return render_template('sales/create.html', customers=customers, items=items, today=today)


@sales_bp.route('/<int:sale_id>/view')
@login_required
def view_sale(sale_id):
    """View sale details"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template('sales/view.html', sale=sale)


@sales_bp.route('/<int:sale_id>/update-payment', methods=['POST'])
@login_required
def update_payment(sale_id):
    """Update payment for sale"""
    sale = Sale.query.get_or_404(sale_id)
    
    payment_amount = float(request.form.get('payment_amount', 0))
    new_due_date = request.form.get('due_date')
    
    if payment_amount < 0:
        flash('Payment amount cannot be negative!', 'danger')
        return redirect(url_for('sales.view_sale', sale_id=sale_id))
    
    if payment_amount > sale.remaining_payment:
        flash(f'Payment amount cannot exceed remaining payment of ₹{sale.remaining_payment:.2f}!', 'danger')
        return redirect(url_for('sales.view_sale', sale_id=sale_id))
    
    # Update sale
    old_remaining = sale.remaining_payment
    sale.advance_payment += payment_amount
    sale.remaining_payment -= payment_amount
    
    if sale.remaining_payment == 0:
        sale.status = 'completed'
    
    # Update due date if provided
    if new_due_date and new_due_date.strip():
        sale.due_date = datetime.strptime(new_due_date, '%Y-%m-%d').date()
    
    sale.updated_by = current_user.user_id
    
    # Update customer balance
    customer = Customer.query.get(sale.customer_id)
    if customer:
        customer.current_balance -= payment_amount
    
    # Update money record
    money = Money.query.filter_by(reference_type='sale', reference_id=sale_id).first()
    if money:
        money.advance_payment = sale.advance_payment
        money.pay_status = 'paid' if sale.remaining_payment == 0 else 'partial' if sale.advance_payment > 0 else 'pending'
        if new_due_date and new_due_date.strip():
            money.due_date = datetime.strptime(new_due_date, '%Y-%m-%d').date()
        money.updated_by = current_user.user_id
    
    db.session.commit()
    
    log_action(current_user.user_id, 'sales', sale_id, 'update', f'Payment updated: ₹{payment_amount:.2f}. Remaining: ₹{old_remaining:.2f} → ₹{sale.remaining_payment:.2f}')
    flash(f'Payment of ₹{payment_amount:.2f} recorded successfully!', 'success')
    return redirect(url_for('sales.view_sale', sale_id=sale_id))


@sales_bp.route('/<int:sale_id>/delete', methods=['POST'])
@login_required
def delete_sale(sale_id):
    """Delete sale"""
    sale = Sale.query.get_or_404(sale_id)
    
    # Revert inventory changes
    for sale_item in sale.items:
        inventory = Inventory.query.filter_by(item_id=sale_item.item_id).first()
        if inventory:
            inventory.current_stock += sale_item.quantity
    
    # Update customer balance
    customer = Customer.query.get(sale.customer_id)
    customer.current_balance -= sale.remaining_payment
    
    log_action(current_user.user_id, 'sales', sale.sale_id, 'delete', f'Deleted sale ID: {sale_id}')
    
    db.session.delete(sale)
    db.session.commit()
    
    flash('Sale deleted successfully!', 'success')
    return redirect(url_for('sales.list_sales'))
