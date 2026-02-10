import math

NM_TO_FT: float = 6076.12


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


def minutes_for_distance(distance_nm: float, speed_kt: float) -> float:
    return (distance_nm / speed_kt) * 60.0


def distance_for_minutes(time_min: float, speed_kt: float) -> float:
    return (speed_kt * time_min) / 60.0
