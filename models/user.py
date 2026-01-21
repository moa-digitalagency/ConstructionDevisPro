from models.base import db, TimestampMixin
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum


class RoleType(enum.Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    METREUR = 'metreur'
    COMMERCIAL = 'commercial'
    READONLY = 'readonly'


class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    can_manage_users = db.Column(db.Boolean, default=False)
    can_manage_bpu = db.Column(db.Boolean, default=False)
    can_manage_projects = db.Column(db.Boolean, default=False)
    can_manage_quotes = db.Column(db.Boolean, default=False)
    can_export = db.Column(db.Boolean, default=False)
    can_view_only = db.Column(db.Boolean, default=False)
    max_margin_percentage = db.Column(db.Numeric(5, 2), nullable=True)
    
    users = db.relationship('UserRole', back_populates='role')


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_company_owner = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    company = db.relationship('Company', back_populates='users')
    roles = db.relationship('UserRole', back_populates='user', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.email
    
    def has_permission(self, permission):
        for user_role in self.roles:
            if getattr(user_role.role, permission, False):
                return True
        return False
    
    def get_role_names(self):
        return [ur.role.name for ur in self.roles]


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    user = db.relationship('User', back_populates='roles')
    role = db.relationship('Role', back_populates='users')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )


class AuditLog(db.Model, TimestampMixin):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    user = db.relationship('User', back_populates='audit_logs')
