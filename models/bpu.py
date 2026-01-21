from models.base import db, TimestampMixin
from datetime import datetime


class BPULibrary(db.Model, TimestampMixin):
    __tablename__ = 'bpu_libraries'
    
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(2), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    effective_date = db.Column(db.Date)
    
    articles = db.relationship('BPUArticle', back_populates='library', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('country', 'version', name='uq_bpu_country_version'),
    )


class BPUArticle(db.Model, TimestampMixin):
    __tablename__ = 'bpu_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('bpu_libraries.id'), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    designation = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    unit_price_eco = db.Column(db.Numeric(12, 2))
    unit_price_standard = db.Column(db.Numeric(12, 2))
    unit_price_premium = db.Column(db.Numeric(12, 2))
    labor_percentage = db.Column(db.Numeric(5, 2), default=0)
    materials_percentage = db.Column(db.Numeric(5, 2), default=0)
    sort_order = db.Column(db.Integer, default=0)
    
    library = db.relationship('BPULibrary', back_populates='articles')
    
    __table_args__ = (
        db.UniqueConstraint('library_id', 'code', name='uq_bpu_article_code'),
    )


class CompanyBPUOverride(db.Model, TimestampMixin):
    __tablename__ = 'company_bpu_overrides'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('bpu_articles.id'), nullable=False)
    designation_override = db.Column(db.Text)
    unit_price_eco = db.Column(db.Numeric(12, 2))
    unit_price_standard = db.Column(db.Numeric(12, 2))
    unit_price_premium = db.Column(db.Numeric(12, 2))
    is_disabled = db.Column(db.Boolean, default=False)
    
    company = db.relationship('Company', back_populates='bpu_overrides')
    article = db.relationship('BPUArticle')
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'article_id', name='uq_company_article_override'),
    )


class CompanyBPUArticle(db.Model, TimestampMixin):
    __tablename__ = 'company_bpu_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    designation = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    unit_price_eco = db.Column(db.Numeric(12, 2))
    unit_price_standard = db.Column(db.Numeric(12, 2))
    unit_price_premium = db.Column(db.Numeric(12, 2))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    company = db.relationship('Company', back_populates='custom_articles')
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'code', name='uq_company_custom_article_code'),
    )
