from datetime import datetime
from app import db
from app.models.log import Log


def log_action(user_id, table_name, record_id, action_taken, description=None):
    """Helper function to create log entries"""
    try:
        log = Log(
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            action_taken=action_taken,
            description=description,
            action_date=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging action: {str(e)}")
        db.session.rollback()
