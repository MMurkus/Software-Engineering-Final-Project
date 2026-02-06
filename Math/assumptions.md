# Project Assumptions

This document lists all fixed assumptions used throughout the Panther Cloud Air project. These assumptions apply globally and do not change during simulation.

## Fixed Hubs
The only hub airports in the system are:
- JFK (New York)
- EWR (Newark)
- LGA (LaGuardia)
- LAX (Los Angeles)

All maintenance, high-capacity gate allocation, and international routing are restricted to these hubs.

## Distance Source
- All inter-airport distances are read directly from `distances.json`
- Distances are provided in nautical miles
- No great-circle or haversine calculations are performed during simulation

## Passenger Demand
- Passenger demand is sourced directly from `travelers.csv`
- Values represent daily travelers per origin–destination pair
- No proportional demand estimation is performed once this file is used

## Aircraft Performance
- Climb angle: 6 degrees
- Acceleration rate: 25 knots per minute
- Deceleration rate: 35 knots per minute
- Cruise speed: 80% of maximum aircraft speed
- Descent rule: 1,000 feet per 3 nautical miles

## Operational Rules
- Minimum flight distance: 150 miles
- Minimum connection time: 30 minutes
- Taxi fuel burn is ignored
- Aircraft must end the day at their starting airport

## Pricing
- Ticket pricing assumes 30% load factor
- Actual passengers may exceed this value, increasing revenue

## Out of Scope
- Crew scheduling
- Real-time optimization
- Detailed weather modeling
- Aircraft-specific performance variations beyond provided rules
