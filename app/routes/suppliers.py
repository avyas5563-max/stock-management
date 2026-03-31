from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.supplier import Supplier
from app.models.purchase import Purchase
from app.utils.logger import log_action

suppliers_bp = Blueprint('suppliers', __name__)


@suppliers_bp.route('/')
@login_required
def list_suppliers():
    """List all suppliers"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Supplier.query
    if search:
        query = query.filter(Supplier.supplier_name.ilike(f'%{search}%'))
    
    suppliers = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('suppliers/list.html', suppliers=suppliers, search=search)


@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_supplier():
    """Create new supplier"""
    if request.method == 'POST':
        supplier_name = request.form.get('supplier_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        supplier = Supplier(
            supplier_name=supplier_name,
            phone=phone,
            address=address,
            current_balance=0.0,
            created_by=current_user.user_id
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        log_action(current_user.user_id, 'suppliers', supplier.supplier_id, 'create', f'Created supplier: {supplier_name}')
        flash('Supplier created successfully!', 'success')
        return redirect(url_for('suppliers.list_suppliers'))
    
    return render_template('suppliers/create.html')


@suppliers_bp.route('/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    """Edit supplier"""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'POST':
        supplier.supplier_name = request.form.get('supplier_name')
        supplier.phone = request.form.get('phone')
        supplier.address = request.form.get('address')
        supplier.updated_by = current_user.user_id
        
        db.session.commit()
        
        log_action(current_user.user_id, 'suppliers', supplier.supplier_id, 'update', f'Updated supplier: {supplier.supplier_name}')
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('suppliers.list_suppliers'))
    
    return render_template('suppliers/edit.html', supplier=supplier)


@suppliers_bp.route('/<int:supplier_id>/view')
@login_required
def view_supplier(supplier_id):
    """View supplier details"""
    supplier = Supplier.query.get_or_404(supplier_id)
    purchases = supplier.purchases.order_by(Purchase.created_at.desc()).limit(10).all()
    return render_template('suppliers/view.html', supplier=supplier, purchases=purchases)


@suppliers_bp.route('/<int:supplier_id>/delete', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    """Delete supplier"""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Check if supplier has purchases
    if supplier.purchases.count() > 0:
        flash('Cannot delete supplier with existing purchases!', 'danger')
        return redirect(url_for('suppliers.list_suppliers'))
    
    log_action(current_user.user_id, 'suppliers', supplier.supplier_id, 'delete', f'Deleted supplier: {supplier.supplier_name}')
    
    db.session.delete(supplier)
    db.session.commit()
    
    flash('Supplier deleted successfully!', 'success')
    return redirect(url_for('suppliers.list_suppliers'))
