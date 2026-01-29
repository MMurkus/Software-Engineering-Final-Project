import math
from definitions import NM_TO_FT


def knots_to_ft_per_min(knots: float) -> float:
    """Convert speed in knots (nmi/hr) to feet per minute."""
    return knots * NM_TO_FT / 60.0


def nautical_miles_to_feet(nmi: float) -> float:
    """Convert distance in nautical miles to feet."""
    return nmi * NM_TO_FT


def feet_to_nautical_miles(feet: float) -> float:
    """Convert distance in feet to nautical miles."""
    return feet / NM_TO_FT


def minutes_to_hours(minutes: float) -> float:
    """Convert minutes to hours."""
    return minutes / 60.0


def hours_to_minutes(hours: float) -> float:
    """Convert hours to minutes."""
    return hours * 60.0
