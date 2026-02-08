from typing import Literal, Optional


class Airplane:
    def __init__(
        self,
        name: Literal["737-600", "737-800", "A220-100", "A220-300"],
        fuel_capacity_gal: float,
        max_speed_kt: float,
        fuel_burn_rate_gal_hr: float,
        max_seats: int,
    ):
        self.name = name
        self.fuel_capacity_gal = fuel_capacity_gal
        self.max_speed_kt = max_speed_kt
        self.fuel_burn_rate_gal_hr = fuel_burn_rate_gal_hr
        self.max_seats = max_seats
        self.current_seats = 0

    def __str__(self):
        return self.name
