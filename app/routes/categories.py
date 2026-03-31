from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.category import Category
from app.utils.logger import log_action

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/')
@login_required
def list_categories():
    """List all categories"""
    page = request.args.get('page', 1, type=int)
    categories = Category.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('categories/list.html', categories=categories)


@categories_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create new category"""
    if request.method == 'POST':
        name = request.form.get('name')
        
        if Category.query.filter_by(name=name).first():
            flash('Category already exists!', 'danger')
            return render_template('categories/create.html')
        
        category = Category(
            name=name,
            created_by=current_user.user_id
        )
        
        db.session.add(category)
        db.session.commit()
        
        log_action(current_user.user_id, 'categories', category.category_id, 'create', f'Created category: {name}')
        flash('Category created successfully!', 'success')
        return redirect(url_for('categories.list_categories'))
    
    return render_template('categories/create.html')


@categories_bp.route('/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Edit category"""
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        # Check if name already exists (excluding current category)
        existing = Category.query.filter_by(name=name).first()
        if existing and existing.category_id != category_id:
            flash('Category name already exists!', 'danger')
            return render_template('categories/edit.html', category=category)
        
        category.name = name
        category.updated_by = current_user.user_id
        
        db.session.commit()
        
        log_action(current_user.user_id, 'categories', category.category_id, 'update', f'Updated category: {name}')
        flash('Category updated successfully!', 'success')
        return redirect(url_for('categories.list_categories'))
    
    return render_template('categories/edit.html', category=category)


@categories_bp.route('/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """Delete category"""
    category = Category.query.get_or_404(category_id)
    
    # Check if category has items
    if category.items.count() > 0:
        flash('Cannot delete category with existing items!', 'danger')
        return redirect(url_for('categories.list_categories'))
    
    log_action(current_user.user_id, 'categories', category.category_id, 'delete', f'Deleted category: {category.name}')
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories.list_categories'))
