from models import db, QuoteVersion, QuoteLine, QuoteAssumption, BPUArticle, CompanyBPUOverride, CompanyBPUArticle, PricingTier, Measurement, Room, ProjectAnswer
from flask_login import current_user
from decimal import Decimal


class QuoteGenerator:
    def __init__(self, project, tier_id=None):
        self.project = project
        self.company = project.company
        self.tier = None
        
        if tier_id:
            self.tier = PricingTier.query.get(tier_id)
        
        if not self.tier:
            self.tier = PricingTier.query.filter_by(
                company_id=self.company.id,
                is_default=True
            ).first()
        
        if not self.tier:
            self.tier = PricingTier.query.filter_by(company_id=self.company.id).first()
        
        self.coefficient = Decimal(str(self.tier.coefficient)) if self.tier else Decimal('1')
        self.vat_rate = self.company.tax_profile.default_vat_rate if self.company.tax_profile else Decimal('20')
    
    def generate_version(self, quote):
        version = QuoteVersion(
            quote_id=quote.id,
            version_number=quote.current_version,
            tier_id=self.tier.id if self.tier else None,
            vat_rate=self.vat_rate,
            created_by_id=current_user.id
        )
        db.session.add(version)
        db.session.flush()
        
        self._generate_lines(version)
        self._generate_assumptions(version)
        self._calculate_totals(version)
        
        return version
    
    def _generate_lines(self, version):
        rooms = Room.query.filter_by(project_id=self.project.id).all()
        measurements = Measurement.query.join(Room).filter(
            Room.project_id == self.project.id
        ).all()
        
        answers = {a.question.code: a for a in self.project.answers}
        
        sort_order = 0
        
        if self.project.project_type.value == 'construction':
            sort_order = self._add_gros_oeuvre_lines(version, rooms, sort_order)
        
        if self.project.project_type.value == 'renovation':
            if 'demolition' in answers and answers['demolition'].answer_value == 'oui':
                sort_order = self._add_demolition_lines(version, rooms, sort_order)
        
        sort_order = self._add_second_oeuvre_lines(version, rooms, answers, sort_order)
        
        if 'clim' in answers and answers['clim'].answer_value != 'aucune':
            sort_order = self._add_hvac_lines(version, answers, sort_order)
        
        if 'piscine' in answers and answers['piscine'].answer_value == 'oui':
            sort_order = self._add_pool_lines(version, answers, sort_order)
    
    def _add_gros_oeuvre_lines(self, version, rooms, sort_order):
        total_area = sum(float(r.area or 0) for r in rooms)
        
        line = QuoteLine(
            version_id=version.id,
            category='Gros Œuvre',
            designation='Fondations et infrastructure',
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=Decimal('350') * self.coefficient,
            total_price=Decimal(str(total_area)) * Decimal('350') * self.coefficient,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        sort_order += 1
        
        line = QuoteLine(
            version_id=version.id,
            category='Gros Œuvre',
            designation='Élévation des murs et structure',
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=Decimal('450') * self.coefficient,
            total_price=Decimal(str(total_area)) * Decimal('450') * self.coefficient,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        sort_order += 1
        
        return sort_order
    
    def _add_demolition_lines(self, version, rooms, sort_order):
        total_area = sum(float(r.area or 0) for r in rooms)
        
        line = QuoteLine(
            version_id=version.id,
            category='Démolition',
            designation='Démolition et évacuation des gravats',
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=Decimal('80') * self.coefficient,
            total_price=Decimal(str(total_area)) * Decimal('80') * self.coefficient,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        return sort_order + 1
    
    def _add_second_oeuvre_lines(self, version, rooms, answers, sort_order):
        total_area = sum(float(r.area or 0) for r in rooms)
        
        line = QuoteLine(
            version_id=version.id,
            category='Second Œuvre',
            designation='Plomberie et sanitaires',
            unit='ens',
            quantity=Decimal('1'),
            unit_price=Decimal(str(total_area * 45)) * self.coefficient,
            total_price=Decimal(str(total_area * 45)) * self.coefficient,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        sort_order += 1
        
        line = QuoteLine(
            version_id=version.id,
            category='Second Œuvre',
            designation='Électricité générale',
            unit='ens',
            quantity=Decimal('1'),
            unit_price=Decimal(str(total_area * 55)) * self.coefficient,
            total_price=Decimal(str(total_area * 55)) * self.coefficient,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        sort_order += 1
        
        floor_type = answers.get('floor_type', None)
        floor_price = Decimal('120')
        if floor_type and floor_type.answer_value:
            floor_prices = {'carrelage': 120, 'parquet': 180, 'marbre': 350, 'beton_cire': 150}
            floor_price = Decimal(str(floor_prices.get(floor_type.answer_value, 120)))
        
        line = QuoteLine(
            version_id=version.id,
            category='Second Œuvre',
            designation='Revêtement de sol',
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=floor_price * self.coefficient,
            total_price=Decimal(str(total_area)) * floor_price * self.coefficient,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        sort_order += 1
        
        return sort_order
    
    def _add_hvac_lines(self, version, answers, sort_order):
        clim_type = answers.get('clim', None)
        clim_qty = answers.get('clim_qty', None)
        
        qty = int(clim_qty.answer_value) if clim_qty and clim_qty.answer_value else 1
        
        if clim_type and clim_type.answer_value == 'split':
            unit_price = Decimal('8500')
            designation = 'Climatisation split'
        else:
            unit_price = Decimal('25000')
            designation = 'Climatisation gainable'
        
        line = QuoteLine(
            version_id=version.id,
            category='CVC',
            designation=designation,
            unit='u',
            quantity=Decimal(str(qty)),
            unit_price=unit_price * self.coefficient,
            total_price=Decimal(str(qty)) * unit_price * self.coefficient,
            quantity_source='manual',
            sort_order=sort_order
        )
        db.session.add(line)
        return sort_order + 1
    
    def _add_pool_lines(self, version, answers, sort_order):
        pool_data = answers.get('piscine_dims', None)
        
        if pool_data and pool_data.answer_data:
            dims = pool_data.answer_data
            length = float(dims.get('length', 8))
            width = float(dims.get('width', 4))
            area = length * width
        else:
            area = 32
        
        line = QuoteLine(
            version_id=version.id,
            category='Piscine',
            designation='Piscine complète (structure, filtration, revêtement)',
            unit='m²',
            quantity=Decimal(str(area)),
            unit_price=Decimal('3500') * self.coefficient,
            total_price=Decimal(str(area)) * Decimal('3500') * self.coefficient,
            quantity_source='manual',
            sort_order=sort_order
        )
        db.session.add(line)
        return sort_order + 1
    
    def _generate_assumptions(self, version):
        answers = self.project.answers
        
        for answer in answers:
            assumption = QuoteAssumption(
                version_id=version.id,
                category=answer.question.category,
                description=answer.question.question_text,
                value=answer.answer_value,
                is_confirmed=answer.is_confirmed,
                source='question_engine'
            )
            db.session.add(assumption)
        
        assumption = QuoteAssumption(
            version_id=version.id,
            category='Général',
            description='Gamme de prix appliquée',
            value=self.tier.name if self.tier else 'Standard',
            is_confirmed=True,
            source='system'
        )
        db.session.add(assumption)
    
    def _calculate_totals(self, version):
        lines = QuoteLine.query.filter_by(version_id=version.id).all()
        
        version.subtotal_ht = sum(line.total_price for line in lines)
        version.vat_amount = version.subtotal_ht * version.vat_rate / 100
        version.total_ttc = version.subtotal_ht + version.vat_amount
