from models import db, QuoteVersion, QuoteLine, QuoteAssumption, BPUArticle, CompanyBPUOverride, CompanyBPUArticle, PricingTier, BPULibrary, Measurement, Room, ProjectAnswer
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

    def _get_article_data(self, code, default_category, default_designation, default_unit, default_price):
        """
        Retrieves article price and designation from BPU based on code and current tier.
        Falls back to default values if not found.
        """
        price = default_price * self.coefficient
        designation = default_designation
        article_id = None
        custom_article_id = None

        # 1. Try Custom Article (Company BPU)
        custom_article = CompanyBPUArticle.query.filter_by(
            company_id=self.company.id,
            code=code,
            is_active=True
        ).first()

        if custom_article:
            custom_article_id = custom_article.id
            designation = custom_article.designation
            # Get price from the column matching the tier (eco/std/prem)
            price_col = self.tier.price_column
            base_price = getattr(custom_article, price_col)
            if base_price is not None:
                price = Decimal(str(base_price)) * self.coefficient
            return price, designation, article_id, custom_article_id

        # 2. Try Library Article (Standard BPU)
        library_article = BPUArticle.query.join(BPULibrary).filter(
            BPUArticle.code == code,
            BPULibrary.country == self.company.country,
            BPULibrary.is_active == True
        ).first()

        if library_article:
            article_id = library_article.id
            designation = library_article.designation

            # Check for Override
            override = CompanyBPUOverride.query.filter_by(
                company_id=self.company.id,
                article_id=library_article.id
            ).first()

            price_col = self.tier.price_column

            if override and not override.is_disabled:
                if override.designation_override:
                    designation = override.designation_override

                # Check if override has a specific price for this tier
                override_price = getattr(override, price_col)
                if override_price is not None:
                    price = Decimal(str(override_price)) * self.coefficient
                else:
                    # Fallback to library price if override doesn't specify this tier
                    base_price = getattr(library_article, price_col)
                    if base_price is not None:
                        price = Decimal(str(base_price)) * self.coefficient
            elif override and override.is_disabled:
                # If explicitly disabled, treat as not found (or return defaults)
                # But here we fallback to defaults passed in arguments
                pass
            else:
                base_price = getattr(library_article, price_col)
                if base_price is not None:
                    price = Decimal(str(base_price)) * self.coefficient

        return price, designation, article_id, custom_article_id
    
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
        
        # Fondations
        price, designation, art_id, cust_id = self._get_article_data(
            'GO-FOND', 'Gros Œuvre', 'Fondations et infrastructure', 'm²', Decimal('350')
        )

        line = QuoteLine(
            version_id=version.id,
            category='Gros Œuvre',
            designation=designation,
            article_id=art_id,
            custom_article_id=cust_id,
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=price,
            total_price=Decimal(str(total_area)) * price,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        sort_order += 1
        
        # Murs
        price, designation, art_id, cust_id = self._get_article_data(
            'GO-MUR', 'Gros Œuvre', 'Élévation des murs et structure', 'm²', Decimal('450')
        )

        line = QuoteLine(
            version_id=version.id,
            category='Gros Œuvre',
            designation=designation,
            article_id=art_id,
            custom_article_id=cust_id,
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=price,
            total_price=Decimal(str(total_area)) * price,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        sort_order += 1
        
        return sort_order
    
    def _add_demolition_lines(self, version, rooms, sort_order):
        total_area = sum(float(r.area or 0) for r in rooms)
        
        price, designation, art_id, cust_id = self._get_article_data(
            'DEMO-01', 'Démolition', 'Démolition et évacuation des gravats', 'm²', Decimal('80')
        )

        line = QuoteLine(
            version_id=version.id,
            category='Démolition',
            designation=designation,
            article_id=art_id,
            custom_article_id=cust_id,
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=price,
            total_price=Decimal(str(total_area)) * price,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        return sort_order + 1
    
    def _add_second_oeuvre_lines(self, version, rooms, answers, sort_order):
        total_area = sum(float(r.area or 0) for r in rooms)
        
        # Plomberie
        # Note: Logic here was 45 * total_area per "ensemble". This is weird.
        # Usually unit price is 45/m2, quantity is area.
        # But existing code set quantity=1, unit_price = area * 45.
        # I will change it to quantity=area, unit_price=45 for better BPU sync.

        price, designation, art_id, cust_id = self._get_article_data(
            'SO-PLOMB', 'Second Œuvre', 'Plomberie et sanitaires (ratio)', 'm²', Decimal('45')
        )

        line = QuoteLine(
            version_id=version.id,
            category='Second Œuvre',
            designation=designation,
            article_id=art_id,
            custom_article_id=cust_id,
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=price,
            total_price=Decimal(str(total_area)) * price,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        sort_order += 1
        
        # Electricité
        price, designation, art_id, cust_id = self._get_article_data(
            'SO-ELEC', 'Second Œuvre', 'Électricité générale (ratio)', 'm²', Decimal('55')
        )

        line = QuoteLine(
            version_id=version.id,
            category='Second Œuvre',
            designation=designation,
            article_id=art_id,
            custom_article_id=cust_id,
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=price,
            total_price=Decimal(str(total_area)) * price,
            quantity_source='calculated',
            sort_order=sort_order
        )
        db.session.add(line)
        sort_order += 1
        
        # Sol
        floor_type = answers.get('floor_type', None)
        default_price = Decimal('120')
        code = 'SO-SOL-STD'

        if floor_type and floor_type.answer_value:
            floor_prices = {'carrelage': 120, 'parquet': 180, 'marbre': 350, 'beton_cire': 150}
            floor_codes = {
                'carrelage': 'SO-SOL-CARR',
                'parquet': 'SO-SOL-PARQ',
                'marbre': 'SO-SOL-MARB',
                'beton_cire': 'SO-SOL-BETON'
            }
            default_price = Decimal(str(floor_prices.get(floor_type.answer_value, 120)))
            code = floor_codes.get(floor_type.answer_value, 'SO-SOL-STD')

        price, designation, art_id, cust_id = self._get_article_data(
            code, 'Second Œuvre', 'Revêtement de sol', 'm²', default_price
        )
        
        line = QuoteLine(
            version_id=version.id,
            category='Second Œuvre',
            designation=designation,
            article_id=art_id,
            custom_article_id=cust_id,
            unit='m²',
            quantity=Decimal(str(total_area)),
            unit_price=price,
            total_price=Decimal(str(total_area)) * price,
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
            default_price = Decimal('8500')
            default_des = 'Climatisation split'
            code = 'CVC-SPLIT'
        else:
            default_price = Decimal('25000')
            default_des = 'Climatisation gainable'
            code = 'CVC-GAIN'

        price, designation, art_id, cust_id = self._get_article_data(
            code, 'CVC', default_des, 'u', default_price
        )
        
        line = QuoteLine(
            version_id=version.id,
            category='CVC',
            designation=designation,
            article_id=art_id,
            custom_article_id=cust_id,
            unit='u',
            quantity=Decimal(str(qty)),
            unit_price=price,
            total_price=Decimal(str(qty)) * price,
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
        
        price, designation, art_id, cust_id = self._get_article_data(
            'EXT-PISCINE', 'Piscine', 'Piscine complète (structure, filtration, revêtement)', 'm²', Decimal('3500')
        )

        line = QuoteLine(
            version_id=version.id,
            category='Piscine',
            designation=designation,
            article_id=art_id,
            custom_article_id=cust_id,
            unit='m²',
            quantity=Decimal(str(area)),
            unit_price=price,
            total_price=Decimal(str(area)) * price,
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
