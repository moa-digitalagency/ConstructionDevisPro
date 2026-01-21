import re


def validate_email(email):
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    if not phone:
        return True
    
    cleaned = re.sub(r'[\s\-\.\(\)]', '', phone)
    
    pattern = r'^\+?[0-9]{8,15}$'
    return bool(re.match(pattern, cleaned))


def validate_password(password):
    if not password or len(password) < 8:
        return False, 'Le mot de passe doit contenir au moins 8 caractères.'
    
    return True, None


def validate_slug(slug):
    if not slug:
        return False
    
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))
