from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.customer import Customer
from app.models.sale import Sale
from app.utils.logger import log_action

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/')
@login_required
def list_customers():
    """List all customers"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Customer.query
    if search:
        query = query.filter(Customer.name.ilike(f'%{search}%'))
    
    customers = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('customers/list.html', customers=customers, search=search)


@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_customer():
    """Create new customer"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        customer = Customer(
            name=name,
            phone=phone,
            address=address,
            current_balance=0.0,
            created_by=current_user.user_id
        )
        
        db.session.add(customer)
        db.session.commit()
        
        log_action(current_user.user_id, 'customers', customer.customer_id, 'create', f'Created customer: {name}')
        flash('Customer created successfully!', 'success')
        return redirect(url_for('customers.list_customers'))
    
    return render_template('customers/create.html')


@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    """Edit customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.phone = request.form.get('phone')
        customer.address = request.form.get('address')
        customer.updated_by = current_user.user_id
        
        db.session.commit()
        
        log_action(current_user.user_id, 'customers', customer.customer_id, 'update', f'Updated customer: {customer.name}')
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customers.list_customers'))
    
    return render_template('customers/edit.html', customer=customer)


@customers_bp.route('/<int:customer_id>/view')
@login_required
def view_customer(customer_id):
    """View customer details"""
    customer = Customer.query.get_or_404(customer_id)
    sales = customer.sales.order_by(Sale.created_at.desc()).limit(10).all()
    return render_template('customers/view.html', customer=customer, sales=sales)


@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    """Delete customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    # Check if customer has sales
    if customer.sales.count() > 0:
        flash('Cannot delete customer with existing sales!', 'danger')
        return redirect(url_for('customers.list_customers'))
    
    log_action(current_user.user_id, 'customers', customer.customer_id, 'delete', f'Deleted customer: {customer.name}')
    
    db.session.delete(customer)
    db.session.commit()
    
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers.list_customers'))
