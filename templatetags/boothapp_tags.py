from django import template

register = template.Library()

@register.filter(name='rp')
def format_rupiah(value):
    """
    Memformat angka menjadi format Rupiah Indonesia.
    Contoh: 1500000 -> Rp 1.500.000
    """
    try:
        val = int(float(value)) if value else 0
    except (ValueError, TypeError):
        val = 0
    
    formatted = f"{val:,}".replace(",", ".")
    return f"Rp {formatted}"