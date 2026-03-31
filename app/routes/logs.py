from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.log import Log
from app.models.user import User
from app import db

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/')
@login_required
def list_logs():
    """List all logs"""
    page = request.args.get('page', 1, type=int)
    table_filter = request.args.get('table', '')
    action_filter = request.args.get('action', '')
    
    query = Log.query
    
    if table_filter:
        query = query.filter(Log.table_name == table_filter)
    
    if action_filter:
        query = query.filter(Log.action_taken == action_filter)
    
    logs = query.order_by(Log.action_date.desc()).paginate(page=page, per_page=50, error_out=False)
    
    # Get unique table names and actions for filters
    tables = db.session.query(Log.table_name).distinct().all()
    tables = [t[0] for t in tables]
    
    actions = ['create', 'update', 'delete', 'login', 'logout']
    
    return render_template('logs/list.html', 
                         logs=logs, 
                         tables=tables, 
                         actions=actions,
                         table_filter=table_filter,
                         action_filter=action_filter)


@logs_bp.route('/<int:log_id>/view')
@login_required
def view_log(log_id):
    """View log details"""
    log = Log.query.get_or_404(log_id)
    return render_template('logs/view.html', log=log)
