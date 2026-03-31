from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.logger import log_action

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
def list_users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('users/list.html', users=users)


@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create new user"""
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        status = request.form.get('status', 'active')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return render_template('users/create.html')
        
        user = User(
            name=name,
            username=username,
            password=generate_password_hash(password),
            role=role,
            status=status,
            created_by=current_user.user_id
        )
        
        db.session.add(user)
        db.session.commit()
        
        log_action(current_user.user_id, 'users', user.user_id, 'create', f'Created user: {username}')
        flash('User created successfully!', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/create.html')


@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.role = request.form.get('role')
        user.status = request.form.get('status')
        user.updated_by = current_user.user_id
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.password = generate_password_hash(new_password)
        
        db.session.commit()
        
        log_action(current_user.user_id, 'users', user.user_id, 'update', f'Updated user: {user.username}')
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/edit.html', user=user)


@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    if user.user_id == current_user.user_id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('users.list_users'))
    
    log_action(current_user.user_id, 'users', user.user_id, 'delete', f'Deleted user: {user.username}')
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users.list_users'))
