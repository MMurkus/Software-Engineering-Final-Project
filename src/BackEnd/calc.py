import json
import math
import csv
import os
from typing import Union, Optional, Callable, Literal, Any
import requests
from datetime import datetime, timedelta
import zoneinfo
from collections import defaultdict
from geopy.distance import great_circle  # type: ignore
from geographiclib.geodesic import Geodesic
from definitions import (
    ACCELERATION_RATE_AT_CRUISING as ACCELERATION_RATE_AT_CRUISING,
    AIRCRAFT_ASCEND_ANGLE_IN_DEGREES as AIRCRAFT_ASCEND_ANGLE_IN_DEGREES,
    ANGLE_OF_ASCENSION_IN_DEGREES as ANGLE_OF_ASCENSION_IN_DEGREES,
    API_TOKEN as API_TOKEN,
    CSV_ROOT as CSV_ROOT,
    DISTANCE_IN_NM_TO_10000FT as DISTANCE_IN_NM_TO_10000FT,
    DISTANCE_IN_NM_TRAVELED_WHILE_ACCEL_TO_280KT as DISTANCE_IN_NM_TRAVELED_WHILE_ACCEL_TO_280KT,
    FLIGHT_CRUISING_1500_MILES_IN_FT as FLIGHT_CRUISING_1500_MILES_IN_FT,
    FLIGHT_CRUISING_INTERNATIONAL_IN_FT as FLIGHT_CRUISING_INTERNATIONAL_IN_FT,
    FLIGHT_CRUISING_LESS_THAN_1500_MILES_IN_FT as FLIGHT_CRUISING_LESS_THAN_1500_MILES_IN_FT,
    FLIGHT_CRUISING_LESS_THAN_200_MILES_IN_FT as FLIGHT_CRUISING_LESS_THAN_200_MILES_IN_FT,
    FLIGHT_CRUISING_LESS_THAN_350_MILES_IN_FT as FLIGHT_CRUISING_LESS_THAN_350_MILES_IN_FT,
    FR_TAKEOFF_LANDING_FEE_USD as FR_TAKEOFF_LANDING_FEE_USD,
    FUEL_COST_FR_TO_USD as FUEL_COST_FR_TO_USD,
    FUEL_COST_USD as FUEL_COST_USD,
    HUBS as HUBS,
    ICAO_TO_METRO_POPULATION as ICAO_TO_METRO_POPULATION,
    ICAO_TO_TIMEZONE as ICAO_TO_TIMEZONE,
    JSON_ROOT as JSON_ROOT,
    KNOTS_TO_FT_PER_MIN as KNOTS_TO_FT_PER_MIN,
    MARKET_SHARE as MARKET_SHARE,
    METERS_PER_NM as METERS_PER_NM,
    MIN_MILES as MIN_MILES,
    PERCENT_OF_FLYERS as PERCENT_OF_FLYERS,
    RATE_OF_ASCEND_IN_MIN_AT_280KT as RATE_OF_ASCEND_IN_MIN_AT_280KT,
    RATE_OF_DESCEND as RATE_OF_DESCEND,
    REFUEL_TIME as REFUEL_TIME,
    SPEED_IN_KNOTS_AT_CRUISING as SPEED_IN_KNOTS_AT_CRUISING,
    SPEED_IN_KNOTS_TO_DESCEND as SPEED_IN_KNOTS_TO_DESCEND,
    TIME_TO_10000FT as TIME_TO_10000FT,
    TIME_TO_ACCEL_TO_280KT as TIME_TO_ACCEL_TO_280KT,
    TIME_TO_DESCEND_TO_GROUND as TIME_TO_DESCEND_TO_GROUND,
    TIME_TO_LIFTOFF as TIME_TO_LIFTOFF,
    TIME_TO_STOP as TIME_TO_STOP,
    TURNAROUND_TIME as TURNAROUND_TIME,
    US_TAKEOFF_LANDING_FEE_USD as US_TAKEOFF_LANDING_FEE_USD,
    WESTBOUND_TIME_MULTIPLIER as WESTBOUND_TIME_MULTIPLIER,
    os as os,
    script_dir as script_dir,
)

from math_utils import (
    NM_TO_FT as NM_TO_FT,
    distance_for_minutes as distance_for_minutes,
    feet_to_nautical_miles as feet_to_nautical_miles,
    hours_to_minutes as hours_to_minutes,
    knots_to_ft_per_min as knots_to_ft_per_min,
    minutes_for_distance as minutes_for_distance,
    minutes_to_hours as minutes_to_hours,
    nautical_miles_to_feet as nautical_miles_to_feet,
)

from classes import Airplane

Boeing_737_600 = Airplane("737-600", 6_875, 485, 850, 149)
Boeing_737_800 = Airplane("737-800", 6_875, 485, 1_050, 189)
Airbus_A220_100 = Airplane("A220-100", 5_700, 470, 700, 135)
Airbus_A220_300 = Airplane("A220-300", 5_700, 470, 750, 160)


def main() -> None:
    HUBS.add("KATL")
    HUBS.add("KDFW")
    HUBS.add("KDEN")

    airports = load_data(f"{JSON_ROOT}/airports.json", fetch_and_mark_airports)
    airport_coords: dict[str, dict] = {}

    for airport, airport_data in airports.items():
        icao, latitude, longitude = (
            airport,
            airport_data.get("latitude_deg"),
            airport_data.get("longitude_deg"),
        )

        if not latitude or not longitude:
            raise ValueError(f"[-] Unable fetch GPS data for {airport}")

        airport_coords[icao] = {"latitude_deg": latitude, "longitude_deg": longitude}

    distances = load_data(
        f"{JSON_ROOT}/distances.json", lambda: calc_distances(airport_coords)
    )

    calc_number_of_flyers(distances)

    for key in ICAO_TO_TIMEZONE.values():
        get_time_of_city(key)

    get_best_hub_locations()

    taxi_times: dict[str, float] = load_data(
        f"{JSON_ROOT}/taxi-times.json", lambda: calc_taxi_time(airports)
    )

    Boeing_737_600_flight_times = calc_flight_times(
        airport_coords, taxi_times, Boeing_737_600, distances
    )
    Boeing_737_800_flight_times = calc_flight_times(
        airport_coords, taxi_times, Boeing_737_800, distances
    )
    Airbus_A220_100_flight_times = calc_flight_times(
        airport_coords, taxi_times, Airbus_A220_100, distances
    )
    Airbus_A220_300_flight_times = calc_flight_times(
        airport_coords, taxi_times, Airbus_A220_300, distances
    )

    calc_flight_cost_and_fuel_usage(Boeing_737_600_flight_times, Boeing_737_600)
    calc_flight_cost_and_fuel_usage(Boeing_737_800_flight_times, Boeing_737_800)
    calc_flight_cost_and_fuel_usage(Airbus_A220_100_flight_times, Airbus_A220_100)
    calc_flight_cost_and_fuel_usage(Airbus_A220_300_flight_times, Airbus_A220_300)


def get_flight_cruising_altitude(
    source_airport: str, dest_airport: str, distances: dict[str, dict]
) -> int:
    distance = distances[source_airport][dest_airport]

    if dest_airport == "LFPG" or source_airport == "LFPG":
        return FLIGHT_CRUISING_INTERNATIONAL_IN_FT
    elif distance >= 1_500:  # IDK If this should be great cuz the docs says "of"
        return FLIGHT_CRUISING_1500_MILES_IN_FT
    elif distance < 350 and distance >= 200:
        return FLIGHT_CRUISING_LESS_THAN_350_MILES_IN_FT
    else:
        return FLIGHT_CRUISING_LESS_THAN_200_MILES_IN_FT


def get_best_hub_locations() -> None:
    counts = defaultdict(int)
    with open(f"{CSV_ROOT}/travelers.csv", "r") as f:
        counts = defaultdict(int)
        reader = csv.DictReader(f)
        for row in reader:
            for col_name, value in row.items():
                try:
                    counts[col_name] += int(value)
                except ValueError:
                    continue

        with open(f"{JSON_ROOT}/hubs.json", "w") as f:
            json.dump(
                {
                    city_name: value
                    for city_name, value in sorted(
                        counts.items(), key=lambda x: x[-1], reverse=True
                    )
                },
                f,
            )


def load_data(
    filename: str,
    build_func: Callable[[], dict],
    post_processs_func: Optional[Callable[[], Any]] = None,
) -> dict:
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return json.load(f)
    data: dict = build_func()
    with open(filename, "w") as f:
        json.dump(data, f)
    return data


# ASSUMES DEST_AIRPORT IS NOT FULL


def minutes_to_hhmmss(total_minutes: float) -> str:
    return str(timedelta(seconds=round(total_minutes * 60)))


def calc_flight_times(
    airport_coords: dict,
    taxi_times: dict,
    airplane_specs: Airplane,
    distances: dict[str, dict],
) -> dict[str, dict[str, dict[str, float]]]:

    airport_flight_times: dict[str, dict[str, dict[str, float]]] = {}
    plane = airplane_specs.name
    airport_flight_times[plane] = {}

    with (
        open(
            f"{CSV_ROOT}/times/decimal/{airplane_specs.name}_times.csv", "w", newline=""
        ) as f_min,
        open(
            f"{CSV_ROOT}/times/human/{airplane_specs.name}_human_times.csv",
            "w",
            newline="",
        ) as f_hms,
    ):
        w_min = csv.writer(f_min)
        w_hms = csv.writer(f_hms)

        header = [""] + list(ICAO_TO_TIMEZONE.keys())
        w_min.writerow(header)
        w_hms.writerow(header)

        for source_airport in airport_coords:
            airport_flight_times[plane][source_airport] = {}

            row_min: list[float] = []
            row_hms: list[str] = []

            for dest_airport in airport_coords:
                if source_airport == dest_airport:
                    row_min.append(0.0)
                    row_hms.append("00:00:00")
                    airport_flight_times[plane][source_airport][dest_airport] = 0.0
                    continue
                cruising_altitude: int = get_flight_cruising_altitude(
                    source_airport, dest_airport, distances
                )
                total_distance_nm, initial_bearing_deg = (
                    geodesic_distance_and_bearing_nm(
                        airport_coords, source_airport, dest_airport
                    )
                )

                must_refuel = False  # TODO: Change

                total_time_min: float = TURNAROUND_TIME + (
                    REFUEL_TIME if must_refuel else 0.0
                )

                total_time_min += TIME_TO_LIFTOFF + TIME_TO_10000FT

                climb_distance_nm, climb_time_min = calc_time_and_distance_to_cruising(
                    cruising_altitude
                )
                total_time_min += climb_time_min

                descent_dist_nm, descent_time_min = (
                    calc_time_and_distance_from_cruising(cruising_altitude)
                )

                accel_time_min = (
                    airplane_specs.max_speed_kt - SPEED_IN_KNOTS_AT_CRUISING
                ) / ACCELERATION_RATE_AT_CRUISING

                accel_dist_nm = distance_for_minutes(
                    accel_time_min,
                    (SPEED_IN_KNOTS_AT_CRUISING + airplane_specs.max_speed_kt) / 2.0,
                )

                remaining_distance_nm = (
                    total_distance_nm
                    - climb_distance_nm
                    - accel_dist_nm
                    - descent_dist_nm
                )

                cruise_time_min = minutes_for_distance(
                    remaining_distance_nm, airplane_specs.max_speed_kt * 0.8
                )

                total_time_min += accel_time_min + cruise_time_min
                total_time_min += (
                    descent_time_min + TIME_TO_STOP + taxi_times[dest_airport]
                )

                initial_bearing_deg %= 360.0

                # Get absolute distance between bearing and westO
                dist_from_west = abs(initial_bearing_deg - 270.0)
                # Get shortest distance to 270* on either side of the angle
                dist_from_west = min(dist_from_west, 360.0 - dist_from_west)

                # Invert so 0 distance = 1
                west_percentage = 1.0 - (dist_from_west / 90.0)

                # If dist_from_west = 0 then west_percentage = 1 and multiply multiplers by * else decrease
                west_percentage = 0 if west_percentage < 0 else west_percentage
                west_time_change_multiplier = 1 + (
                    WESTBOUND_TIME_MULTIPLIER * west_percentage
                )
                total_time_min *= west_time_change_multiplier

                total_time_min = round(total_time_min, 2)

                row_min.append(total_time_min)
                row_hms.append(minutes_to_hhmmss(total_time_min))

                airport_flight_times[plane][source_airport][dest_airport] = (
                    total_time_min
                )

            w_min.writerow([source_airport] + row_min)
            w_hms.writerow([source_airport] + row_hms)

    return airport_flight_times


def geodesic_distance_and_bearing_nm(
    airport_coords: dict,
    source_airport: str,
    dest_airport: str,
) -> tuple[float, float]:
    lat1 = airport_coords[source_airport]["latitude_deg"]
    lon1 = airport_coords[source_airport]["longitude_deg"]
    lat2 = airport_coords[dest_airport]["latitude_deg"]
    lon2 = airport_coords[dest_airport]["longitude_deg"]

    geodesic = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
    distance_nm = geodesic["s12"] / METERS_PER_NM
    bearing_deg = geodesic["azi1"] % 360.0

    return distance_nm, bearing_deg


def calc_time_and_distance_cruise_transition(
    cruising_altitude: Literal[38_000, 35_000, 30_000, 25_000, 20_000],
    *,
    direction: Literal["to", "from"],
) -> tuple[float, float]:
    height_ft: float = cruising_altitude - 10_000

    if direction == "to":
        total_distance_nm = feet_to_nautical_miles(
            height_ft / math.sin(math.radians(AIRCRAFT_ASCEND_ANGLE_IN_DEGREES))
        )
        remaining_distance = (
            total_distance_nm - DISTANCE_IN_NM_TRAVELED_WHILE_ACCEL_TO_280KT
        )

        return (
            total_distance_nm,
            TIME_TO_ACCEL_TO_280KT
            + remaining_distance / RATE_OF_ASCEND_IN_MIN_AT_280KT,
        )

    elif direction == "from":
        # direction == "from" (descent): 3 NM per 1000 ft
        total_distance_nm = (height_ft / 1000.0) * 3.0

        return (
            total_distance_nm,
            total_distance_nm / RATE_OF_ASCEND_IN_MIN_AT_280KT,
        )


def calc_time_and_distance_to_cruising(
    cruising_altitude: Literal[38_000, 35_000, 30_000, 25_000, 20_000],
) -> tuple[float, float]:
    return calc_time_and_distance_cruise_transition(cruising_altitude, direction="to")


def calc_time_and_distance_from_cruising(
    cruising_altitude: Literal[38_000, 35_000, 30_000, 25_000, 20_000],
) -> tuple[float, float]:
    return calc_time_and_distance_cruise_transition(cruising_altitude, direction="from")


def calc_distances(airport_coords: dict) -> dict:
    distances_csv: dict = {}
    distances_json: dict[str, dict[str, float]] = defaultdict(dict)

    with open(
        f"{CSV_ROOT}/distances.csv",
        "w",
    ) as f:
        # TODO: This should be exported to a func but I'm too lazy
        writer = csv.writer(f)
        writer.writerow([""] + list(ICAO_TO_TIMEZONE.keys()))
        for source_airport, source_coords in airport_coords.items():
            source_airport_coords = (
                source_coords["latitude_deg"],
                source_coords["longitude_deg"],
            )
            row: list[Union[float, str]] = []
            for dest_airport, dest_coords in airport_coords.items():
                dest_airport_coords = (
                    dest_coords["latitude_deg"],
                    dest_coords["longitude_deg"],
                )
                if source_airport == dest_airport:
                    row.append(0.00)
                    continue

                miles: float = (
                    great_circle(
                        source_airport_coords,
                        dest_airport_coords,
                    ).miles
                    * 0.8689758
                )

                row.append(round(miles, 5) if miles >= MIN_MILES else -1.000)

                distances_json[source_airport][dest_airport] = (
                    round(miles, 5) if miles >= MIN_MILES else -1.000
                )

            distances_csv[source_airport] = row
            writer.writerow([source_airport] + row)
    return distances_json


"""
Format of timezone expected : "America/New_York" | "Europe/Paris"
"""

"""
DOES NOT ACCOUNT FOR FULL GATES 
"""


def hub_taxi_time(population: float) -> float:
    if population <= 9_000_000:
        return 15
    extra = math.ceil((population - 9_000_000) / 2_000_000)
    return min(20, 15 + extra)


def calc_taxi_time(airports_data: dict) -> dict:
    taxi_times: dict[str, float] = {}
    for current_icao, current_population in ICAO_TO_METRO_POPULATION.items():
        if not airports_data[current_icao]["is_hub"]:
            taxi_times[current_icao] = min(13, current_population * 0.0000075)
        else:
            taxi_times[current_icao] = hub_taxi_time(current_population)

    return taxi_times


def get_time_of_city(iana_time_zone: str) -> datetime:
    local_timezone = zoneinfo.ZoneInfo(iana_time_zone)
    local_time = datetime.now(local_timezone)
    print(f"Time in ({iana_time_zone.split('/')[-1]}) : ", end="")
    print(
        local_time.strftime("%Y-%m-%d %H:%M:%S ")
    )  # Could add %Z timezone zone (e.g UTC,EST), %z outputs the UTC Offset
    return local_time


def calc_total_reachable_airport_populations(
    source_airport_name: str,
    distances: dict[str, dict[str, float]],
) -> float:
    # TODO: FILTER for reachable using distances and time
    populations_counter: float = 0.0
    for dest_airport_name, nautical_miles in distances[source_airport_name].items():
        if source_airport_name == dest_airport_name:
            continue
        if nautical_miles >= MIN_MILES:
            populations_counter += ICAO_TO_METRO_POPULATION[dest_airport_name]
    print(f"[+] Total Population from {source_airport_name} : {populations_counter}")

    return populations_counter


def calc_number_of_flyers(
    airport_distances: dict[str, dict[str, float]],
):
    with open(
        f"{CSV_ROOT}/travelers.csv",
        "w",
    ) as f:
        writer = csv.writer(f)
        writer.writerow([""] + list(ICAO_TO_METRO_POPULATION.keys()))

        for (
            source_city_name,
            source_city_population,
        ) in ICAO_TO_METRO_POPULATION.items():
            total_reachable_population = calc_total_reachable_airport_populations(
                source_city_name,
                airport_distances,
            )
            daily_flyers = source_city_population * PERCENT_OF_FLYERS
            panther_flyers = daily_flyers * MARKET_SHARE
            row: list[int] = []
            for (
                distination_city_name,
                destination_city_population,
            ) in ICAO_TO_METRO_POPULATION.items():
                if source_city_name != distination_city_name:
                    dest_share = (
                        destination_city_population / total_reachable_population
                    )
                    row.append(round(panther_flyers * dest_share))
                else:
                    row.append(0)
            writer.writerow([source_city_name] + row)


"""
Fetches airport data from random api that uses wikipedia and adds attributes "is_hub" to that data and returns that data as dict to write to airports.json
"""


def fetch_and_mark_airports() -> dict:
    fetched_airports_data = fetch_airports()
    return mark_airports_as_hubs(fetched_airports_data)


def mark_airports_as_hubs(fetched_airports_data: dict) -> dict:
    for icao in fetched_airports_data:
        fetched_airports_data[icao]["is_hub"] = icao in HUBS
        if icao in HUBS:
            print(f"[+] Marked {icao} as hub")
    return fetched_airports_data


def calc_flight_cost_and_fuel_usage(
    flight_times_by_airplane: dict, airplane_specs: Airplane
) -> dict:
    with open(
        f"{CSV_ROOT}/costs/{airplane_specs.name}_costs.csv",
        "w",
    ) as f:
        writer = csv.writer(f)
        writer.writerow([""] + list(ICAO_TO_METRO_POPULATION.keys()))

        flight_costs = {}
        for source_airport in flight_times_by_airplane[airplane_specs.name]:
            flight_costs[source_airport] = {}
            takeoff_fee = (
                FR_TAKEOFF_LANDING_FEE_USD
                if source_airport == "LFPG"
                else US_TAKEOFF_LANDING_FEE_USD
            )
            fuel_price = (
                FUEL_COST_FR_TO_USD if source_airport == "LFPG" else FUEL_COST_USD
            )

            row: list[int] = []
            for dest_airport in flight_times_by_airplane[airplane_specs.name][
                source_airport
            ]:
                if source_airport == dest_airport:
                    flight_costs[source_airport][dest_airport] = 0.00
                    row.append(0.00)
                    continue
                flight_time_hr = (
                    flight_times_by_airplane[airplane_specs.name][source_airport][
                        dest_airport
                    ]
                    / 60.0
                )

                gallons_used = flight_time_hr * airplane_specs.fuel_burn_rate_gal_hr
                fuel_cost = gallons_used * fuel_price

                landing_fee = (
                    FR_TAKEOFF_LANDING_FEE_USD
                    if dest_airport == "LFPG"
                    else US_TAKEOFF_LANDING_FEE_USD
                )
                total_cost = round(fuel_cost + takeoff_fee + landing_fee, 2)
                flight_costs[source_airport][dest_airport] = total_cost
                row.append(total_cost)
            writer.writerow([source_airport] + row)

    return flight_costs


def calc_profits(flight_costs: dict) -> dict: ...


def fetch_airports() -> dict:
    airline_data = {}
    for icao in ICAO_TO_TIMEZONE.keys():
        url = f"https://airportdb.io/api/v1/airport/{icao}?apiToken={API_TOKEN}"
        print(f"[+] Fetching {icao} ({url})")
        request = requests.get(url, timeout=30)
        airline_data[icao] = request.json()

    return airline_data


if __name__ == "__main__":
    main()
