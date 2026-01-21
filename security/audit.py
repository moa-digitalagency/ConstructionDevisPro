from flask import request
from flask_login import current_user
from models import db, AuditLog


def log_action(action, entity_type, entity_id=None, old_values=None, new_values=None):
    try:
        if not current_user.is_authenticated:
            return
        
        audit_log = AuditLog(
            user_id=current_user.id,
            company_id=current_user.company_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:500] if request.user_agent else None
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Audit log error: {e}")
