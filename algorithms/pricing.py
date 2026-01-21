from decimal import Decimal, ROUND_HALF_UP


def apply_tier_coefficient(base_price, coefficient, rounding=2):
    if base_price is None:
        return Decimal('0')
    
    try:
        price = Decimal(str(base_price))
        coef = Decimal(str(coefficient))
        result = price * coef
        
        if rounding >= 0:
            quantize_str = '0.' + '0' * rounding
            result = result.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)
        
        return result
    except:
        return Decimal('0')


def calculate_line_total(quantity, unit_price):
    if quantity is None or unit_price is None:
        return Decimal('0')
    
    try:
        qty = Decimal(str(quantity))
        price = Decimal(str(unit_price))
        return (qty * price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except:
        return Decimal('0')


def calculate_quote_totals(lines, vat_rate=20.0, discount_percentage=0.0):
    subtotal_ht = Decimal('0')
    
    for line in lines:
        if hasattr(line, 'total_price'):
            subtotal_ht += Decimal(str(line.total_price or 0))
        elif isinstance(line, dict):
            subtotal_ht += Decimal(str(line.get('total_price', 0)))
    
    if discount_percentage:
        discount = subtotal_ht * Decimal(str(discount_percentage)) / 100
        subtotal_ht = subtotal_ht - discount
    else:
        discount = Decimal('0')
    
    vat = subtotal_ht * Decimal(str(vat_rate)) / 100
    vat = vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    total_ttc = subtotal_ht + vat
    
    return {
        'subtotal_ht': subtotal_ht,
        'discount_amount': discount,
        'vat_amount': vat,
        'total_ttc': total_ttc
    }


def calculate_margin(cost_price, selling_price):
    if not cost_price or not selling_price:
        return Decimal('0')
    
    try:
        cost = Decimal(str(cost_price))
        sell = Decimal(str(selling_price))
        
        if sell == 0:
            return Decimal('0')
        
        margin = ((sell - cost) / sell) * 100
        return margin.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except:
        return Decimal('0')
