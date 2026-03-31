from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.inventory import Inventory
from app.models.item import Item
from app.models.purchase import PurchaseItem
from app.models.sale import SaleItem
from app import db
from app.utils.logger import log_action

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/')
@login_required
def list_inventory():
    """List all inventory"""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')
    
    query = db.session.query(Inventory, Item).join(Item, Inventory.item_id == Item.item_id)
    
    if filter_type == 'low_stock':
        query = query.filter(Inventory.current_stock < Item.min_stock)
    elif filter_type == 'out_of_stock':
        query = query.filter(Inventory.current_stock == 0)
    
    inventory = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('inventory/list.html', inventory=inventory, filter_type=filter_type)


@inventory_bp.route('/<int:item_id>/details')
@login_required
def inventory_details(item_id):
    """View inventory details for an item"""
    item = Item.query.get_or_404(item_id)
    inventory = Inventory.query.filter_by(item_id=item_id).first()
    
    # Get recent purchase and sale items
    recent_purchases = item.purchase_items.order_by(PurchaseItem.created_at.desc()).limit(10).all()
    recent_sales = item.sale_items.order_by(SaleItem.created_at.desc()).limit(10).all()
    
    return render_template('inventory/details.html', 
                         item=item, 
                         inventory=inventory,
                         recent_purchases=recent_purchases,
                         recent_sales=recent_sales)


@inventory_bp.route('/<int:item_id>/add-stock', methods=['POST'])
@login_required
def add_stock(item_id):
    """Manually add stock to inventory"""
    item = Item.query.get_or_404(item_id)
    inventory = Inventory.query.filter_by(item_id=item_id).first()
    
    quantity = request.form.get('quantity', type=int)
    reason = request.form.get('reason', 'Manual stock addition')
    
    if not quantity or quantity <= 0:
        flash('Please enter a valid quantity!', 'danger')
        return redirect(url_for('inventory.list_inventory'))
    
    # Create or update inventory
    if not inventory:
        inventory = Inventory(item_id=item_id, current_stock=0)
        db.session.add(inventory)
    
    old_stock = inventory.current_stock
    inventory.current_stock += quantity
    
    db.session.commit()
    
    log_action(current_user.user_id, 'inventory', item_id, 'update', 
               f'Added {quantity} {item.unit} to {item.item_name}. Stock: {old_stock} → {inventory.current_stock}. Reason: {reason}')
    
    flash(f'Successfully added {quantity} {item.unit} to {item.item_name}!', 'success')
    return redirect(url_for('inventory.list_inventory'))


@inventory_bp.route('/<int:item_id>/remove-stock', methods=['POST'])
@login_required
def remove_stock(item_id):
    """Manually remove stock from inventory"""
    item = Item.query.get_or_404(item_id)
    inventory = Inventory.query.filter_by(item_id=item_id).first()
    
    if not inventory:
        flash('No inventory record found!', 'danger')
        return redirect(url_for('inventory.list_inventory'))
    
    quantity = request.form.get('quantity', type=int)
    reason = request.form.get('reason', 'Manual stock removal')
    
    if not quantity or quantity <= 0:
        flash('Please enter a valid quantity!', 'danger')
        return redirect(url_for('inventory.list_inventory'))
    
    if inventory.current_stock < quantity:
        flash(f'Insufficient stock! Current stock: {inventory.current_stock} {item.unit}', 'danger')
        return redirect(url_for('inventory.list_inventory'))
    
    old_stock = inventory.current_stock
    inventory.current_stock -= quantity
    
    db.session.commit()
    
    log_action(current_user.user_id, 'inventory', item_id, 'update', 
               f'Removed {quantity} {item.unit} from {item.item_name}. Stock: {old_stock} → {inventory.current_stock}. Reason: {reason}')
    
    flash(f'Successfully removed {quantity} {item.unit} from {item.item_name}!', 'success')
    return redirect(url_for('inventory.list_inventory'))


@inventory_bp.route('/<int:item_id>/adjust-stock', methods=['POST'])
@login_required
def adjust_stock(item_id):
    """Adjust inventory stock to exact amount"""
    item = Item.query.get_or_404(item_id)
    inventory = Inventory.query.filter_by(item_id=item_id).first()
    
    new_stock = request.form.get('new_stock', type=int)
    reason = request.form.get('reason', 'Manual stock adjustment')
    
    if new_stock is None or new_stock < 0:
        flash('Please enter a valid stock quantity!', 'danger')
        return redirect(url_for('inventory.list_inventory'))
    
    # Create or update inventory
    if not inventory:
        inventory = Inventory(item_id=item_id, current_stock=0)
        db.session.add(inventory)
    
    old_stock = inventory.current_stock
    inventory.current_stock = new_stock
    
    db.session.commit()
    
    log_action(current_user.user_id, 'inventory', item_id, 'update', 
               f'Adjusted stock for {item.item_name}. Stock: {old_stock} → {new_stock}. Reason: {reason}')
    
    flash(f'Successfully adjusted stock for {item.item_name} to {new_stock} {item.unit}!', 'success')
    return redirect(url_for('inventory.list_inventory'))
