# Revenue and Profit Calculations

This document describes ticket pricing, revenue, and profit calculations.

## Seating
Each aircraft has a fixed number of seats based on type.

## Pricing Assumption
Ticket prices are calculated assuming:
- 30% load factor

fare per seat =
total flight cost / (0.30 × seats)

## Revenue
actual revenue =
fare per seat × actual boarded passengers

Actual boarded passengers may exceed 30% load factor.

## Profit
profit =
revenue − total operating cost

This allows the simulation to reflect increased profitability at higher load factors.
