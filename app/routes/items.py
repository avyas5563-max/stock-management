from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.item import Item
from app.models.category import Category
from app.models.inventory import Inventory
from app.utils.logger import log_action

items_bp = Blueprint('items', __name__)


@items_bp.route('/')
@login_required
def list_items():
    """List all items"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Item.query
    if search:
        query = query.filter(Item.item_name.ilike(f'%{search}%'))
    
    items = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('items/list.html', items=items, search=search)


@items_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_item():
    """Create new item"""
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        category_id = request.form.get('category_id')
        unit = request.form.get('unit')
        purchase_price = float(request.form.get('purchase_price', 0))
        sale_price = float(request.form.get('sale_price', 0))
        min_stock = float(request.form.get('min_stock', 0))
        
        item = Item(
            item_name=item_name,
            category_id=category_id,
            unit=unit,
            purchase_price=purchase_price,
            sale_price=sale_price,
            min_stock=min_stock,
            created_by=current_user.user_id
        )
        
        db.session.add(item)
        db.session.flush()  # Get item_id
        
        # Create inventory entry
        inventory = Inventory(
            item_id=item.item_id,
            current_stock=0.0,
            created_by=current_user.user_id
        )
        db.session.add(inventory)
        db.session.commit()
        
        log_action(current_user.user_id, 'items', item.item_id, 'create', f'Created item: {item_name}')
        flash('Item created successfully!', 'success')
        return redirect(url_for('items.list_items'))
    
    categories = Category.query.all()
    return render_template('items/create.html', categories=categories)


@items_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Edit item"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        item.item_name = request.form.get('item_name')
        item.category_id = request.form.get('category_id')
        item.unit = request.form.get('unit')
        item.purchase_price = float(request.form.get('purchase_price', 0))
        item.sale_price = float(request.form.get('sale_price', 0))
        item.min_stock = float(request.form.get('min_stock', 0))
        item.updated_by = current_user.user_id
        
        db.session.commit()
        
        log_action(current_user.user_id, 'items', item.item_id, 'update', f'Updated item: {item.item_name}')
        flash('Item updated successfully!', 'success')
        return redirect(url_for('items.list_items'))
    
    categories = Category.query.all()
    return render_template('items/edit.html', item=item, categories=categories)


@items_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    """Delete item"""
    item = Item.query.get_or_404(item_id)
    
    # Check if item has any sales
    if item.sale_items.count() > 0:
        flash('Cannot delete item with existing sales records!', 'danger')
        return redirect(url_for('items.list_items'))
    
    # Check if item has any purchases
    if item.purchase_items.count() > 0:
        flash('Cannot delete item with existing purchase records!', 'danger')
        return redirect(url_for('items.list_items'))
    
    # Delete inventory record first
    inventory = Inventory.query.filter_by(item_id=item_id).first()
    if inventory:
        db.session.delete(inventory)
    
    log_action(current_user.user_id, 'items', item.item_id, 'delete', f'Deleted item: {item.item_name}')
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('items.list_items'))
