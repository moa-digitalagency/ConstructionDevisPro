from models.base import db, TimestampMixin
from datetime import datetime
import enum


class ProjectType(enum.Enum):
    CONSTRUCTION = 'construction'
    RENOVATION = 'renovation'
    EXTENSION = 'extension'
    AMENAGEMENT = 'amenagement'


class ProjectTypology(enum.Enum):
    VILLA = 'villa'
    IMMEUBLE = 'immeuble'
    RIAD = 'riad'
    BUREAU = 'bureau'
    COMMERCE = 'commerce'
    APPARTEMENT = 'appartement'
    AUTRE = 'autre'


class ProjectStatus(enum.Enum):
    DRAFT = 'draft'
    IN_PROGRESS = 'in_progress'
    PENDING_QUESTIONS = 'pending_questions'
    QUOTE_READY = 'quote_ready'
    COMPLETED = 'completed'
    ARCHIVED = 'archived'


class Project(db.Model, TimestampMixin):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    reference = db.Column(db.String(50))
    client_name = db.Column(db.String(255))
    client_email = db.Column(db.String(255))
    client_phone = db.Column(db.String(50))
    client_address = db.Column(db.Text)
    project_type = db.Column(db.Enum(ProjectType), nullable=False)
    typology = db.Column(db.Enum(ProjectTypology), nullable=False)
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    default_tier_id = db.Column(db.Integer, db.ForeignKey('pricing_tiers.id'))
    total_surface = db.Column(db.Numeric(12, 2))
    notes = db.Column(db.Text)
    
    company = db.relationship('Company', back_populates='projects')
    default_tier = db.relationship('PricingTier')
    plans = db.relationship('ProjectPlan', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')
    rooms = db.relationship('Room', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')
    quotes = db.relationship('Quote', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')
    answers = db.relationship('ProjectAnswer', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')

    def generate_reference(self):
        year = datetime.utcnow().year
        count = Project.query.filter(
            Project.company_id == self.company_id,
            db.extract('year', Project.created_at) == year
        ).count() + 1
        self.reference = f"PRJ-{year}-{count:04d}"


class ProjectPlan(db.Model, TimestampMixin):
    __tablename__ = 'project_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20))
    file_size = db.Column(db.Integer)
    is_calibrated = db.Column(db.Boolean, default=False)
    scale_factor = db.Column(db.Numeric(10, 6))
    calibration_data = db.Column(db.JSON)
    
    project = db.relationship('Project', back_populates='plans')
    versions = db.relationship('PlanVersion', back_populates='plan', lazy='dynamic', cascade='all, delete-orphan')
    measurements = db.relationship('Measurement', back_populates='plan', lazy='dynamic', cascade='all, delete-orphan')


class PlanVersion(db.Model, TimestampMixin):
    __tablename__ = 'plan_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('project_plans.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False, default=1)
    file_path = db.Column(db.String(500), nullable=False)
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    plan = db.relationship('ProjectPlan', back_populates='versions')
    created_by = db.relationship('User')


class Room(db.Model, TimestampMixin):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('project_plans.id'))
    name = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(50))
    level = db.Column(db.Integer, default=0)
    area = db.Column(db.Numeric(12, 2))
    perimeter = db.Column(db.Numeric(12, 2))
    ceiling_height = db.Column(db.Numeric(5, 2), default=2.80)
    polygon_data = db.Column(db.JSON)
    
    project = db.relationship('Project', back_populates='rooms')
    plan = db.relationship('ProjectPlan')


class Measurement(db.Model, TimestampMixin):
    __tablename__ = 'measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('project_plans.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    measurement_type = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Numeric(12, 4), nullable=False)
    confidence = db.Column(db.String(20), default='medium')
    source = db.Column(db.String(50), default='manual')
    polygon_data = db.Column(db.JSON)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    plan = db.relationship('ProjectPlan', back_populates='measurements')
    room = db.relationship('Room')
    created_by = db.relationship('User')
