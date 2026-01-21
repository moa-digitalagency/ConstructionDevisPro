import math
from decimal import Decimal


def calculate_polygon_area(points, scale_factor=1.0):
    if not points or len(points) < 3:
        return Decimal('0')
    
    n = len(points)
    area = 0.0
    
    for i in range(n):
        j = (i + 1) % n
        area += points[i]['x'] * points[j]['y']
        area -= points[j]['x'] * points[i]['y']
    
    area = abs(area) / 2.0
    
    area_real = area * (scale_factor ** 2)
    
    return Decimal(str(round(area_real, 4)))


def calculate_perimeter(points, scale_factor=1.0):
    if not points or len(points) < 2:
        return Decimal('0')
    
    perimeter = 0.0
    n = len(points)
    
    for i in range(n):
        j = (i + 1) % n
        dx = points[j]['x'] - points[i]['x']
        dy = points[j]['y'] - points[i]['y']
        perimeter += math.sqrt(dx**2 + dy**2)
    
    perimeter_real = perimeter * scale_factor
    
    return Decimal(str(round(perimeter_real, 4)))


def calculate_wall_surface(perimeter, height):
    if not perimeter or not height:
        return Decimal('0')
    
    try:
        p = Decimal(str(perimeter))
        h = Decimal(str(height))
        return p * h
    except:
        return Decimal('0')


def calculate_volume(area, height):
    if not area or not height:
        return Decimal('0')
    
    try:
        a = Decimal(str(area))
        h = Decimal(str(height))
        return a * h
    except:
        return Decimal('0')


def calculate_distance(point1, point2, scale_factor=1.0):
    dx = point2['x'] - point1['x']
    dy = point2['y'] - point1['y']
    distance_pixels = math.sqrt(dx**2 + dy**2)
    
    return Decimal(str(round(distance_pixels * scale_factor, 4)))
