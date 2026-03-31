def format_currency(value):
    """Format number as currency"""
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"


def format_date(value, format='%Y-%m-%d'):
    """Format datetime to string"""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    return value.strftime(format)


def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Format datetime to string with time"""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    return value.strftime(format)
