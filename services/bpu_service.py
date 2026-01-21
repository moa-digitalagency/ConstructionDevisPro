from models import db, BPUArticle, CompanyBPUOverride, CompanyBPUArticle, BPULibrary
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
import io
from decimal import Decimal


class BPUService:
    def __init__(self, company):
        self.company = company
    
    def get_library(self):
        return BPULibrary.query.filter_by(
            country=self.company.country,
            is_active=True
        ).order_by(BPULibrary.version.desc()).first()
    
    def get_article_price(self, article, tier_code='STD'):
        override = CompanyBPUOverride.query.filter_by(
            company_id=self.company.id,
            article_id=article.id
        ).first()
        
        if override:
            if tier_code == 'ECO':
                return override.price_eco or article.price_eco
            elif tier_code == 'PREM':
                return override.price_premium or article.price_premium
            else:
                return override.price_standard or article.price_standard
        
        if tier_code == 'ECO':
            return article.price_eco
        elif tier_code == 'PREM':
            return article.price_premium
        else:
            return article.price_standard
    
    def get_all_articles(self, include_custom=True):
        library = self.get_library()
        if not library:
            return []
        
        articles = list(BPUArticle.query.filter_by(library_id=library.id).all())
        
        if include_custom:
            custom = list(self.company.custom_articles.filter_by(is_active=True).all())
            for c in custom:
                c.is_custom = True
            articles.extend(custom)
        
        return articles
    
    def export_to_excel(self):
        library = self.get_library()
        if not library:
            return None
        
        articles = BPUArticle.query.filter_by(library_id=library.id)\
            .order_by(BPUArticle.category, BPUArticle.sort_order).all()
        
        overrides = {o.article_id: o for o in self.company.bpu_overrides.all()}
        
        wb = Workbook()
        ws = wb.active
        ws.title = 'BPU'
        
        header_fill = PatternFill(start_color='1a56db', end_color='1a56db', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        headers = ['Code', 'Catégorie', 'Désignation', 'Unité', 'Prix Éco', 'Prix Standard', 'Prix Premium', 'Personnalisé']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center')
        
        category_fill = PatternFill(start_color='E3E8EF', end_color='E3E8EF', fill_type='solid')
        
        current_category = ''
        row = 2
        
        for article in articles:
            override = overrides.get(article.id)
            has_override = override is not None
            
            ws.cell(row=row, column=1, value=article.code).border = border
            ws.cell(row=row, column=2, value=article.category).border = border
            ws.cell(row=row, column=3, value=article.designation).border = border
            ws.cell(row=row, column=4, value=article.unit).border = border
            
            price_eco = float(override.price_eco if override and override.price_eco else article.price_eco or 0)
            price_std = float(override.price_standard if override and override.price_standard else article.price_standard or 0)
            price_prem = float(override.price_premium if override and override.price_premium else article.price_premium or 0)
            
            ws.cell(row=row, column=5, value=price_eco).border = border
            ws.cell(row=row, column=6, value=price_std).border = border
            ws.cell(row=row, column=7, value=price_prem).border = border
            ws.cell(row=row, column=8, value='Oui' if has_override else '').border = border
            
            row += 1
        
        for col in range(1, 9):
            ws.column_dimensions[get_column_letter(col)].width = 15
        ws.column_dimensions['C'].width = 50
        
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return buffer
    
    def import_from_excel(self, file_stream):
        try:
            wb = load_workbook(file_stream)
            ws = wb.active
            
            imported = 0
            errors = []
            
            for row in range(2, ws.max_row + 1):
                code = ws.cell(row=row, column=1).value
                if not code:
                    continue
                
                category = ws.cell(row=row, column=2).value or ''
                designation = ws.cell(row=row, column=3).value or ''
                unit = ws.cell(row=row, column=4).value or ''
                price_eco = ws.cell(row=row, column=5).value
                price_std = ws.cell(row=row, column=6).value
                price_prem = ws.cell(row=row, column=7).value
                
                try:
                    existing = CompanyBPUArticle.query.filter_by(
                        company_id=self.company.id,
                        code=code
                    ).first()
                    
                    if existing:
                        existing.category = category
                        existing.designation = designation
                        existing.unit = unit
                        existing.price_eco = Decimal(str(price_eco or 0))
                        existing.price_standard = Decimal(str(price_std or 0))
                        existing.price_premium = Decimal(str(price_prem or 0))
                    else:
                        article = CompanyBPUArticle(
                            company_id=self.company.id,
                            code=code,
                            category=category,
                            designation=designation,
                            unit=unit,
                            price_eco=Decimal(str(price_eco or 0)),
                            price_standard=Decimal(str(price_std or 0)),
                            price_premium=Decimal(str(price_prem or 0))
                        )
                        db.session.add(article)
                    
                    imported += 1
                    
                except Exception as e:
                    errors.append(f'Ligne {row}: {str(e)}')
            
            db.session.commit()
            
            return {
                'success': True,
                'imported': imported,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_override(self, article_id, price_eco=None, price_standard=None, price_premium=None):
        existing = CompanyBPUOverride.query.filter_by(
            company_id=self.company.id,
            article_id=article_id
        ).first()
        
        if existing:
            if price_eco is not None:
                existing.price_eco = price_eco
            if price_standard is not None:
                existing.price_standard = price_standard
            if price_premium is not None:
                existing.price_premium = price_premium
        else:
            override = CompanyBPUOverride(
                company_id=self.company.id,
                article_id=article_id,
                price_eco=price_eco,
                price_standard=price_standard,
                price_premium=price_premium
            )
            db.session.add(override)
        
        db.session.commit()
        return True
    
    def remove_override(self, article_id):
        CompanyBPUOverride.query.filter_by(
            company_id=self.company.id,
            article_id=article_id
        ).delete()
        db.session.commit()
        return True
