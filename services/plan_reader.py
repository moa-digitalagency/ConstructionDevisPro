import os
from PyPDF2 import PdfReader
from PIL import Image
import io
import json


class PlanReader:
    SUPPORTED_FORMATS = ['pdf', 'dwg', 'dxf', 'png', 'jpg', 'jpeg']
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.extension = os.path.splitext(file_path)[1].lower().replace('.', '')
        self.metadata = {}
        self.is_scanned = False
        self.is_vector = False
        self.page_count = 1
        self.dimensions = None
    
    def analyze(self):
        if self.extension == 'pdf':
            return self._analyze_pdf()
        elif self.extension in ['dwg', 'dxf']:
            return self._analyze_cad()
        elif self.extension in ['png', 'jpg', 'jpeg']:
            return self._analyze_image()
        else:
            return {'success': False, 'error': 'Format non supporté'}
    
    def _analyze_pdf(self):
        try:
            reader = PdfReader(self.file_path)
            self.page_count = len(reader.pages)
            
            first_page = reader.pages[0]
            media_box = first_page.mediabox
            self.dimensions = {
                'width': float(media_box.width),
                'height': float(media_box.height),
                'unit': 'pt'
            }
            
            text_content = ''
            for page in reader.pages[:3]:
                text_content += page.extract_text() or ''
            
            self.is_vector = len(text_content.strip()) > 50
            self.is_scanned = not self.is_vector
            
            self.metadata = {
                'page_count': self.page_count,
                'dimensions': self.dimensions,
                'is_vector': self.is_vector,
                'is_scanned': self.is_scanned,
                'has_text': len(text_content.strip()) > 0,
                'format': 'PDF'
            }
            
            return {
                'success': True,
                'metadata': self.metadata,
                'recommendations': self._get_recommendations()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _analyze_cad(self):
        try:
            file_size = os.path.getsize(self.file_path)
            
            self.is_vector = True
            self.is_scanned = False
            
            self.metadata = {
                'page_count': 1,
                'is_vector': True,
                'is_scanned': False,
                'file_size': file_size,
                'format': self.extension.upper(),
                'requires_conversion': True
            }
            
            return {
                'success': True,
                'metadata': self.metadata,
                'recommendations': self._get_cad_recommendations()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _analyze_image(self):
        try:
            with Image.open(self.file_path) as img:
                self.dimensions = {
                    'width': img.width,
                    'height': img.height,
                    'unit': 'px',
                    'dpi': img.info.get('dpi', (72, 72))
                }
            
            self.is_scanned = True
            self.is_vector = False
            
            self.metadata = {
                'page_count': 1,
                'dimensions': self.dimensions,
                'is_vector': False,
                'is_scanned': True,
                'format': self.extension.upper()
            }
            
            return {
                'success': True,
                'metadata': self.metadata,
                'recommendations': self._get_recommendations()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_recommendations(self):
        recs = []
        
        if self.is_scanned:
            recs.append({
                'type': 'info',
                'message': 'Plan scanné détecté. La calibration manuelle est requise.'
            })
            recs.append({
                'type': 'action',
                'message': 'Définissez 2 points de référence avec une distance connue.'
            })
        else:
            recs.append({
                'type': 'success',
                'message': 'Plan vectoriel détecté. Les mesures seront plus précises.'
            })
        
        if self.dimensions:
            width_mm = self.dimensions['width'] * 0.3528 if self.dimensions['unit'] == 'pt' else self.dimensions['width']
            if width_mm > 1000:
                recs.append({
                    'type': 'info',
                    'message': 'Grand format détecté. Vérifiez l\'échelle après calibration.'
                })
        
        return recs
    
    def _get_cad_recommendations(self):
        return [
            {
                'type': 'info',
                'message': f'Fichier {self.extension.upper()} détecté.'
            },
            {
                'type': 'action',
                'message': 'Ce format sera converti en image pour affichage. La calibration est recommandée.'
            }
        ]
    
    def convert_to_image(self, page_number=0, dpi=150):
        if self.extension == 'pdf':
            return self._pdf_to_image(page_number, dpi)
        elif self.extension in ['dwg', 'dxf']:
            return self._cad_to_image()
        elif self.extension in ['png', 'jpg', 'jpeg']:
            return self.file_path
        return None
    
    def _pdf_to_image(self, page_number=0, dpi=150):
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(self.file_path, dpi=dpi, first_page=page_number+1, last_page=page_number+1)
            if images:
                output_path = self.file_path.replace('.pdf', f'_page_{page_number}.png')
                images[0].save(output_path, 'PNG')
                return output_path
        except ImportError:
            return None
        except Exception:
            return None
        return None
    
    def _cad_to_image(self):
        placeholder_path = self.file_path + '_preview.png'
        
        try:
            img = Image.new('RGB', (800, 600), color='white')
            img.save(placeholder_path, 'PNG')
            return placeholder_path
        except Exception:
            return None


def calculate_scale_from_calibration(point1, point2, real_distance_meters):
    import math
    
    px_distance = math.sqrt(
        (point2['x'] - point1['x']) ** 2 +
        (point2['y'] - point1['y']) ** 2
    )
    
    if px_distance == 0:
        return None
    
    meters_per_pixel = real_distance_meters / px_distance
    
    return {
        'meters_per_pixel': meters_per_pixel,
        'pixels_per_meter': 1 / meters_per_pixel,
        'calibration_points': [point1, point2],
        'real_distance': real_distance_meters
    }


def calculate_polygon_area(points, scale):
    if len(points) < 3:
        return 0
    
    n = len(points)
    area_px = 0
    
    for i in range(n):
        j = (i + 1) % n
        area_px += points[i]['x'] * points[j]['y']
        area_px -= points[j]['x'] * points[i]['y']
    
    area_px = abs(area_px) / 2
    
    area_m2 = area_px * (scale['meters_per_pixel'] ** 2)
    
    return round(area_m2, 2)


def calculate_polygon_perimeter(points, scale):
    if len(points) < 2:
        return 0
    
    import math
    
    perimeter_px = 0
    n = len(points)
    
    for i in range(n):
        j = (i + 1) % n
        distance = math.sqrt(
            (points[j]['x'] - points[i]['x']) ** 2 +
            (points[j]['y'] - points[i]['y']) ** 2
        )
        perimeter_px += distance
    
    perimeter_m = perimeter_px * scale['meters_per_pixel']
    
    return round(perimeter_m, 2)
