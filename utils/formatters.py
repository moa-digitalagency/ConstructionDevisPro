from datetime import datetime


def format_currency(amount, currency='MAD', locale='fr'):
    if amount is None:
        return '-'
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return '-'
    
    formatted = f"{amount:,.2f}".replace(',', ' ').replace('.', ',')
    
    return f"{formatted} {currency}"


def format_number(number, decimals=2):
    if number is None:
        return '-'
    
    try:
        number = float(number)
    except (ValueError, TypeError):
        return '-'
    
    if decimals == 0:
        return f"{int(number):,}".replace(',', ' ')
    
    return f"{number:,.{decimals}f}".replace(',', ' ').replace('.', ',')


def format_date(date_value, format_str='%d/%m/%Y'):
    if date_value is None:
        return '-'
    
    if isinstance(date_value, str):
        try:
            date_value = datetime.fromisoformat(date_value)
        except ValueError:
            return date_value
    
    try:
        return date_value.strftime(format_str)
    except AttributeError:
        return str(date_value)


def format_percentage(value, decimals=1):
    if value is None:
        return '-'
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return '-'
    
    return f"{value:.{decimals}f}%"


def format_area(value, unit='m²'):
    if value is None:
        return '-'
    
    return f"{format_number(value, 2)} {unit}"
