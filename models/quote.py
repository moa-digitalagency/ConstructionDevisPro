from models.base import db, TimestampMixin
from datetime import datetime
import enum


class QuoteStatus(enum.Enum):
    DRAFT = 'draft'
    PENDING = 'pending'
    SENT = 'sent'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    EXPIRED = 'expired'


class Quote(db.Model, TimestampMixin):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    reference = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum(QuoteStatus), default=QuoteStatus.DRAFT)
    current_version = db.Column(db.Integer, default=1)
    valid_until = db.Column(db.Date)
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    project = db.relationship('Project', back_populates='quotes')
    versions = db.relationship('QuoteVersion', back_populates='quote', lazy='dynamic', cascade='all, delete-orphan', order_by='QuoteVersion.version_number.desc()')

    def generate_reference(self):
        year = datetime.utcnow().year
        count = Quote.query.join(Project).filter(
            Project.company_id == self.project.company_id,
            db.extract('year', Quote.created_at) == year
        ).count() + 1
        self.reference = f"DEV-{year}-{count:04d}"


class QuoteVersion(db.Model, TimestampMixin):
    __tablename__ = 'quote_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    tier_id = db.Column(db.Integer, db.ForeignKey('pricing_tiers.id'))
    subtotal_ht = db.Column(db.Numeric(14, 2), default=0)
    vat_amount = db.Column(db.Numeric(14, 2), default=0)
    total_ttc = db.Column(db.Numeric(14, 2), default=0)
    vat_rate = db.Column(db.Numeric(5, 2))
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(14, 2), default=0)
    margin_percentage = db.Column(db.Numeric(5, 2), default=0)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pdf_path = db.Column(db.String(500))
    
    quote = db.relationship('Quote', back_populates='versions')
    tier = db.relationship('PricingTier')
    created_by = db.relationship('User')
    lines = db.relationship('QuoteLine', back_populates='version', lazy='dynamic', cascade='all, delete-orphan', order_by='QuoteLine.sort_order')
    assumptions = db.relationship('QuoteAssumption', back_populates='version', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('quote_id', 'version_number', name='uq_quote_version'),
    )


class QuoteLine(db.Model, TimestampMixin):
    __tablename__ = 'quote_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('quote_versions.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('bpu_articles.id'))
    custom_article_id = db.Column(db.Integer, db.ForeignKey('company_bpu_articles.id'))
    category = db.Column(db.String(100))
    designation = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Numeric(12, 4), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    total_price = db.Column(db.Numeric(14, 2), nullable=False)
    measurement_id = db.Column(db.Integer, db.ForeignKey('measurements.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    quantity_source = db.Column(db.String(50), default='manual')
    sort_order = db.Column(db.Integer, default=0)
    
    version = db.relationship('QuoteVersion', back_populates='lines')
    article = db.relationship('BPUArticle')
    custom_article = db.relationship('CompanyBPUArticle')
    measurement = db.relationship('Measurement')
    room = db.relationship('Room')


class QuoteAssumption(db.Model, TimestampMixin):
    __tablename__ = 'quote_assumptions'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('quote_versions.id'), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    value = db.Column(db.String(255))
    is_confirmed = db.Column(db.Boolean, default=False)
    source = db.Column(db.String(50))
    
    version = db.relationship('QuoteVersion', back_populates='assumptions')
