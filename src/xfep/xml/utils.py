"""Utility functions for XML generation: formatting amounts, dates, quantities."""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP


def fmt_amount(value: Decimal | float | int | str) -> str:
    """Format a monetary amount to exactly 2 decimal places.

    SUNAT requires exactly 2 decimal places for all monetary amounts.

    >>> fmt_amount(Decimal("100.1"))
    '100.10'
    >>> fmt_amount(Decimal("99"))
    '99.00'
    """
    d = Decimal(str(value))
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def fmt_quantity(value: Decimal | float | int | str) -> str:
    """Format a quantity, preserving up to 10 decimal places, minimum 3.

    Removes trailing zeros but keeps at least 3 decimal places.

    >>> fmt_quantity(Decimal("5"))
    '5.000'
    >>> fmt_quantity(Decimal("1.5"))
    '1.500'
    >>> fmt_quantity(Decimal("2.12345"))
    '2.12345'
    """
    d = Decimal(str(value))
    # Quantize to 10 decimal places first
    quantized = d.quantize(Decimal("0.0000000001"), rounding=ROUND_HALF_UP)
    # Normalize to remove trailing zeros
    normalized = quantized.normalize()
    # Get string representation
    s = str(normalized)
    # Ensure at least 3 decimal places
    if "." not in s:
        return s + ".000"
    integer_part, decimal_part = s.split(".")
    if len(decimal_part) < 3:
        decimal_part = decimal_part.ljust(3, "0")
    return f"{integer_part}.{decimal_part}"


def fmt_date(d: date) -> str:
    """Format a date as ISO 8601 (YYYY-MM-DD).

    >>> from datetime import date
    >>> fmt_date(date(2026, 1, 15))
    '2026-01-15'
    """
    return d.isoformat()
