"""
constants.py

Contains all consant units throughout our simulation.

"""

# Unit conversions
nm_to_miles = 1.15078  # nautical miles to statute miles
feet_per_nm = 6076  # feet per nautical mile

# Climb / Descent Rules

# Aircraft climbs at a fixed 6 degree angle
climb_angle_deg = 6

# Precomputed tangent of 6 degrees
# Used to convert vertical distance to horizontal distance
tan_climb = 0.105104

# Acceleration and deceleration rates. These came from straight from the project description.
accel_rate = 25  # knots per minute
decel_rate = 35  # knots per minute

# Ground Operations

# Time spent on the runway
takeoff_runway_min = 1  # minutes
landing_runway_min = 2  # minutes


# Earth Rotation Effect


# Eastbound flights are faster
eastbound_factor = 0.955

# Westbound flights are slower
westbound_factor = 1.045


# Fuel and Costs

# Fuel price in the United States ($/gallon)
us_fuel_cost = 6.19

# Fuel price in France ($/liter)
fr_fuel_cost_per_liter = 2.29

# Unit conversion
gallon_to_liter = 3.785

# Airport Fees

us_takeoff_fee = 2000  # dollars
us_landing_fee = 2000  # dollars
fr_landing_fee = 2450  # dollars

# Aircraft Data

# Dictionary allows easy expansion to more aircraft later
aircraft = {
    "A220-300": {
        "seats": 145,  # total passenger seats
        "burn_gph": 800,  # fuel burn (gallons per hour)
        "max_speed": 470,  # max cruise speed (knots)
    }
}
