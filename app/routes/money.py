from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.money import Money
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.sale import Sale
from app.models.purchase import Purchase
from app.utils.logger import log_action

money_bp = Blueprint('money', __name__)


@money_bp.route('/')
@login_required
def list_transactions():
    """List all money transactions"""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')
    
    query = Money.query
    
    if filter_type == 'pending':
        query = query.filter(Money.pay_status == 'pending')
    elif filter_type == 'partial':
        query = query.filter(Money.pay_status == 'partial')
    elif filter_type == 'paid':
        query = query.filter(Money.pay_status == 'paid')
    elif filter_type == 'purchase':
        query = query.filter(Money.reference_type == 'purchase')
    elif filter_type == 'sale':
        query = query.filter(Money.reference_type == 'sale')
    
    transactions = query.order_by(Money.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('money/list.html', transactions=transactions, filter_type=filter_type)


@money_bp.route('/<int:transaction_id>/view')
@login_required
def view_transaction(transaction_id):
    """View transaction details"""
    transaction = Money.query.get_or_404(transaction_id)
    
    # Get party details
    party = None
    if transaction.party_type == 'customer':
        party = Customer.query.get(transaction.party_id)
    elif transaction.party_type == 'supplier':
        party = Supplier.query.get(transaction.party_id)
    
    return render_template('money/view.html', transaction=transaction, party=party)


@money_bp.route('/<int:transaction_id>/update_payment', methods=['POST'])
@login_required
def update_payment(transaction_id):
    """Update payment status and sync with Sale/Purchase"""
    transaction = Money.query.get_or_404(transaction_id)
    
    additional_payment = float(request.form.get('additional_payment', 0))
    
    if additional_payment <= 0:
        flash('Payment amount must be greater than 0!', 'danger')
        return redirect(url_for('money.view_transaction', transaction_id=transaction_id))
    
    # Calculate remaining before update
    remaining_before = transaction.total_amount - transaction.advance_payment
    
    if additional_payment > remaining_before:
        flash(f'Payment amount cannot exceed remaining amount of ₹{remaining_before:.2f}!', 'danger')
        return redirect(url_for('money.view_transaction', transaction_id=transaction_id))
    
    # Update Money transaction
    transaction.advance_payment += additional_payment
    remaining = transaction.total_amount - transaction.advance_payment
    
    if remaining <= 0:
        transaction.pay_status = 'paid'
    elif transaction.advance_payment > 0:
        transaction.pay_status = 'partial'
    
    transaction.updated_by = current_user.user_id
    
    # Sync with Sale or Purchase record
    if transaction.reference_type == 'sale' and transaction.reference_id:
        sale = Sale.query.get(transaction.reference_id)
        if sale:
            sale.advance_payment += additional_payment
            sale.remaining_payment -= additional_payment
            if sale.remaining_payment <= 0:
                sale.remaining_payment = 0
                sale.status = 'completed'
            sale.updated_by = current_user.user_id
    
    elif transaction.reference_type == 'purchase' and transaction.reference_id:
        purchase = Purchase.query.get(transaction.reference_id)
        if purchase:
            purchase.advance_payment += additional_payment
            purchase.remaining_amount -= additional_payment
            if purchase.remaining_amount <= 0:
                purchase.remaining_amount = 0
                purchase.status = 'completed'
            purchase.updated_by = current_user.user_id
    
    # Update party balance
    if transaction.party_type == 'customer':
        customer = Customer.query.get(transaction.party_id)
        if customer:
            customer.current_balance -= additional_payment
    elif transaction.party_type == 'supplier':
        supplier = Supplier.query.get(transaction.party_id)
        if supplier:
            supplier.current_balance -= additional_payment
    
    db.session.commit()
    
    log_action(current_user.user_id, 'money', transaction.transaction_id, 'update', 
              f'Updated payment: Added ₹{additional_payment:.2f}. Remaining: ₹{remaining_before:.2f} → ₹{remaining:.2f}')
    
    flash(f'Payment of ₹{additional_payment:.2f} recorded successfully! Updated in {transaction.reference_type.title()} and Dashboard.', 'success')
    
    return redirect(url_for('money.view_transaction', transaction_id=transaction_id))


@money_bp.route('/<int:transaction_id>/edit_payment_type', methods=['POST'])
@login_required
def edit_payment_type(transaction_id):
    """Edit payment type/mode for a transaction"""
    transaction = Money.query.get_or_404(transaction_id)
    
    new_payment_type = request.form.get('payment_type')
    
    if not new_payment_type:
        flash('Payment type is required!', 'danger')
        return redirect(url_for('money.view_transaction', transaction_id=transaction_id))
    
    old_payment_type = transaction.payment_type
    transaction.payment_type = new_payment_type
    transaction.updated_by = current_user.user_id
    
    # Sync with Sale or Purchase record
    if transaction.reference_type == 'sale' and transaction.reference_id:
        sale = Sale.query.get(transaction.reference_id)
        if sale:
            sale.payment_type = new_payment_type
            sale.updated_by = current_user.user_id
    
    elif transaction.reference_type == 'purchase' and transaction.reference_id:
        purchase = Purchase.query.get(transaction.reference_id)
        if purchase:
            purchase.payment_type = new_payment_type
            purchase.updated_by = current_user.user_id
    
    db.session.commit()
    
    log_action(current_user.user_id, 'money', transaction.transaction_id, 'update', 
              f'Changed payment type: {old_payment_type} → {new_payment_type}')
    
    flash(f'Payment type updated from {old_payment_type} to {new_payment_type} successfully!', 'success')
    
    return redirect(url_for('money.view_transaction', transaction_id=transaction_id))


@money_bp.route('/upcoming_payments')
@login_required
def upcoming_payments():
    """Show upcoming payments"""
    from datetime import date, timedelta
    
    today = date.today()
    next_week = today + timedelta(days=7)
    
    upcoming = Money.query.filter(
        Money.due_date.between(today, next_week),
        Money.pay_status.in_(['pending', 'partial'])
    ).order_by(Money.due_date).all()
    
    return render_template('money/upcoming.html', upcoming=upcoming)
