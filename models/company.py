from models.base import db, TimestampMixin
from datetime import datetime


class Company(db.Model, TimestampMixin):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    country = db.Column(db.String(2), nullable=False, default='MA')
    currency = db.Column(db.String(3), nullable=False, default='MAD')
    is_active = db.Column(db.Boolean, default=True)
    onboarding_completed = db.Column(db.Boolean, default=False)
    onboarding_step = db.Column(db.Integer, default=1)
    
    users = db.relationship('User', back_populates='company', lazy='dynamic')
    branding = db.relationship('CompanyBranding', back_populates='company', uselist=False, cascade='all, delete-orphan')
    tax_profile = db.relationship('TaxProfile', back_populates='company', uselist=False, cascade='all, delete-orphan')
    pricing_tiers = db.relationship('PricingTier', back_populates='company', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', back_populates='company', lazy='dynamic', cascade='all, delete-orphan')
    bpu_overrides = db.relationship('CompanyBPUOverride', back_populates='company', lazy='dynamic', cascade='all, delete-orphan')
    custom_articles = db.relationship('CompanyBPUArticle', back_populates='company', lazy='dynamic', cascade='all, delete-orphan')

    def ensure_default_tiers(self):
        """Creates default pricing tiers if none exist."""
        if self.pricing_tiers.count() > 0:
            return

        # Create default tiers
        tiers = [
            PricingTier(company_id=self.id, name='Économique', code='ECO', coefficient=0.85, is_default=False, sort_order=1),
            PricingTier(company_id=self.id, name='Standard', code='STD', coefficient=1.00, is_default=True, sort_order=2),
            PricingTier(company_id=self.id, name='Premium', code='PREM', coefficient=1.25, is_default=False, sort_order=3),
        ]
        for tier in tiers:
            db.session.add(tier)
        db.session.commit()

    def __repr__(self):
        return f'<Company {self.name}>'


class CompanyBranding(db.Model, TimestampMixin):
    __tablename__ = 'company_brandings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, unique=True)
    logo_path = db.Column(db.String(500))
    primary_color = db.Column(db.String(7), default='#1a56db')
    secondary_color = db.Column(db.String(7), default='#1e40af')
    legal_name = db.Column(db.String(255))
    address = db.Column(db.Text)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    registration_number = db.Column(db.String(100))
    tax_id = db.Column(db.String(100))
    bank_details = db.Column(db.Text)
    quote_footer = db.Column(db.Text)
    quote_terms = db.Column(db.Text)
    
    company = db.relationship('Company', back_populates='branding')


class TaxProfile(db.Model, TimestampMixin):
    __tablename__ = 'tax_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, unique=True)
    default_vat_rate = db.Column(db.Numeric(5, 2), default=20.00)
    vat_included = db.Column(db.Boolean, default=False)
    payment_terms_days = db.Column(db.Integer, default=30)
    payment_conditions = db.Column(db.Text)
    deposit_percentage = db.Column(db.Numeric(5, 2), default=30.00)
    
    company = db.relationship('Company', back_populates='tax_profile')


class PricingTier(db.Model, TimestampMixin):
    __tablename__ = 'pricing_tiers'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    coefficient = db.Column(db.Numeric(5, 2), default=1.00)
    rounding = db.Column(db.Integer, default=2)
    is_default = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    
    company = db.relationship('Company', back_populates='pricing_tiers')
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'code', name='uq_company_tier_code'),
    )

    @property
    def price_column(self):
        """Returns the BPU price column to use based on the tier name."""
        name_lower = self.name.lower()
        if 'eco' in name_lower:
            return 'unit_price_eco'
        elif 'premium' in name_lower or 'luxe' in name_lower:
            return 'unit_price_premium'
        else:
            return 'unit_price_standard'
