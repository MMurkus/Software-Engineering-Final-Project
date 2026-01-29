import json
import math
import csv
import os
from typing import Union, Optional, Callable, Literal, Any
import requests
from datetime import datetime
import zoneinfo
from collections import defaultdict
from geopy.distance import great_circle  # type: ignore
from geographiclib.geodesic import Geodesic
from definitions import *
from math_utils import (
    NMI_TO_FT as NMI_TO_FT,
    feet_to_nautical_miles as feet_to_nautical_miles,
    hours_to_minutes as hours_to_minutes,
    knots_to_ft_per_min as knots_to_ft_per_min,
    minutes_to_hours as minutes_to_hours,
    nautical_miles_to_feet as nautical_miles_to_feet,
)

# import requests
HUBS.add("KATL")
HUBS.add("KDFW")
HUBS.add("KDEN")

ICAO_TO_TIMEZONE = {
    "KATL": "America/New_York",
    "KDFW": "America/Chicago",
    "KDEN": "America/Denver",
    "KORD": "America/Chicago",
    "KLAX": "America/Los_Angeles",
    "KJFK": "America/New_York",
    "KCLT": "America/New_York",
    "KLAS": "America/Los_Angeles",  # Follows Pacific Time of las_vegas
    "KMCO": "America/New_York",
    "KMIA": "America/New_York",
    "KPHX": "America/Phoenix",  # no DST
    "KSEA": "America/Los_Angeles",
    "KSFO": "America/Los_Angeles",
    "KEWR": "America/New_York",
    "KIAH": "America/Chicago",
    "KBOS": "America/New_York",
    "KMSP": "America/Chicago",
    "KFLL": "America/New_York",
    "KLGA": "America/New_York",
    "KDTW": "America/New_York",
    "KPHL": "America/New_York",
    "KSLC": "America/Denver",
    "KBWI": "America/New_York",
    "KIAD": "America/New_York",
    "KSAN": "America/Los_Angeles",
    "KDCA": "America/New_York",
    "KTPA": "America/New_York",
    "KBNA": "America/Chicago",
    "KAUS": "America/Chicago",
    "PHNL": "Pacific/Honolulu",  # Hawaii
    "LFPG": "Europe/Paris",  # Charles de Gaulle
}
ICAO_TO_METRO_POPULATION: dict[str, float] = {
    "KATL": 6_300_000,  # Atlanta
    "KDFW": 7_900_000,  # Dallas–Fort Worth
    "KDEN": 3_000_000,  # Denver
    "KORD": 9_500_000,  # Chicago
    "KLAX": 13_200_000,  # Los Angeles
    "KJFK": 20_200_000,  # New York City
    "KCLT": 2_800_000,  # Charlotte
    "KLAS": 2_300_000,  # Las Vegas
    "KMCO": 2_700_000,  # Orlando
    "KMIA": 6_200_000,  # Miami–Fort Lauderdale
    "KPHX": 5_100_000,  # Phoenix
    "KSEA": 4_100_000,  # Seattle
    "KSFO": 7_800_000,  # San Francisco Bay Area
    "KEWR": 20_200_000,  # NYC metro
    "KIAH": 7_300_000,  # Houston
    "KBOS": 5_000_000,  # Boston
    "KMSP": 3_700_000,  # Minneapolis–St. Paul
    "KFLL": 6_200_000,  # Miami–Fort Lauderdale
    "KLGA": 20_200_000,  # NYC metro
    "KDTW": 4_300_000,  # Detroit
    "KPHL": 6_200_000,  # Philadelphia
    "KSLC": 1_300_000,  # Salt Lake City
    "KBWI": 6_200_000,  # Baltimore–Washington
    "KIAD": 6_200_000,  # Washington DC metro
    "KSAN": 3_300_000,  # San Diego
    "KDCA": 6_200_000,  # Washington DC metro
    "KTPA": 3_200_000,  # Tampa Bay
    "KBNA": 2_000_000,  # Nashville
    "KAUS": 2_400_000,  # Austin
    "PHNL": 1_000_000,  # Honolulu
    "LFPG": 13_000_000,  # Paris metro
}


def main() -> None:
    airports = load_data("./JSONs/airports.json", fetch_and_mark_airports)

    # FIXME: Passing data to every calc

    distances = load_data(
        "./JSONs/distances.json", lambda: calculate_distances(airports)
    )

    calc_number_of_flyers(distances)

    for key in ICAO_TO_TIMEZONE.values():
        get_time_of_city(key)

    get_best_hub_locations()
    taxi_times: dict[str, float] = load_data(
        "./JSONs/taxi-times.json", lambda: calc_taxi_time(airports)
    )

    calc_time_to_ascend_to_target_height(250, 10_000)
    calc_time_to_descend_to_ten_thousand(38000)


# calc_time_to_ascend_to_target_height(250, 20_000, 10000)
# calc_time_to_ascend_to_target_height(250, 25_000, 10000)
# calc_time_to_ascend_to_target_height(250, 30_000, 10000)
# calc_time_to_ascend_to_target_height(250, 35_000, 10000)
# calc_time_to_ascend_to_target_height(250, 38_000, 10000)


def get_best_hub_locations():
    counts = defaultdict(int)
    with open("./CSVs/travelers.csv", "r") as f:
        counts = defaultdict(int)
        reader = csv.DictReader(f)
        for row in reader:
            for col_name, value in row.items():
                try:
                    counts[col_name] += int(value)
                except ValueError:
                    continue

        with open("./JSONs/hubs.json", "w") as f:
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


def calculate_distances(airports: dict) -> dict:
    airport_coords: list[tuple] = []
    distances_csv: dict = {}
    distances_json: dict[str, dict[str, float]] = defaultdict(dict)

    for airport, airport_data in airports.items():
        icao, latitude, longitude = (
            airport,
            airport_data.get("latitude_deg"),
            airport_data.get("longitude_deg"),
        )

        if not latitude or not longitude:
            raise ValueError(f"[-] Unable fetch GPS data for {airport}")

        airport_coords.append((icao, latitude, longitude))

    with open(
        "./CSVs/distances.csv",
        "w",
    ) as f:
        # TODO: This should be exported but I'm too lazy
        writer = csv.writer(f)
        writer.writerow([""] + list(ICAO_TO_TIMEZONE.keys()))

        for source_airport, *source_airport_coords in airport_coords:
            row: list[Union[float, str]] = []
            for dest_airport, *dest_airport_coords in airport_coords:
                if source_airport == dest_airport:
                    row.append(0.00)
                    continue

                miles: float = (
                    great_circle(source_airport_coords, dest_airport_coords).miles
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


def calculate_total_reachable_airport_populations(
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


# TODO: Make return in JSON format like with distances but our get_best_hubs reads the csv file instead
def calc_number_of_flyers(
    airport_distances: dict[str, dict[str, float]],
):
    with open(
        "./CSVs/travelers.csv",
        "w",
    ) as f:
        writer = csv.writer(f)
        writer.writerow([""] + list(ICAO_TO_METRO_POPULATION.keys()))

        for (
            source_city_name,
            source_city_population,
        ) in ICAO_TO_METRO_POPULATION.items():
            total_reachable_population = calculate_total_reachable_airport_populations(
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


def fetch_airports() -> dict:
    airline_data = {}
    for icao in ICAO_TO_TIMEZONE.keys():
        url = f"https://airportdb.io/api/v1/airport/{icao}?apiToken={API_TOKEN}"
        print(f"[+] Fetching {icao} ({url})")
        request = requests.get(url, timeout=30)
        airline_data[icao] = request.json()

    return airline_data


# FIXME:
def calc_flight_time(source_airport: str, dest_airport: str) -> float:
    # result = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
    # initial_bearing = result['azi1']  # Initial bearing in degrees
    # print(f"Bearing: {initial_bearing:.3f}°")
    return -1.0
    ...


def calc_time_to_ascend_to_target_height(
    speed_in_knots: float, target_height: float, ground_level: float = 0
):
    feet_per_minute: float = (
        KNOTS_TO_FT_PER_MIN
        * math.sin(math.radians(ANGLE_OF_ASCENSION_IN_DEGREES))
        * speed_in_knots
    )

    time_to_ascend = (target_height - ground_level) / feet_per_minute
    print(
        f"Time to ascend to {target_height}ft from {ground_level}ft : {time_to_ascend} minutes"
    )

    return time_to_ascend


"""
Returns time in minutes converting from the 1knot = 1nm / hr
"""


def calc_time_to_descend_to_ten_thousand(
    cruising_altitude: Literal[38_000, 35_000, 30_000, 25_000, 20_000],
) -> float:
    time_to_descend = (
        ((cruising_altitude - 10_000) * RATE_OF_DESCEND**-1) / SPEED_IN_KNOTS_TO_DESCEND
    ) * 60

    print(
        f"Time to descend from {cruising_altitude}ft to 10,000ft : {time_to_descend} minutes"
    )
    return time_to_descend


def calc_time_to_crusing(
    cruising_altitude: Literal[38_000, 35_000, 30_000, 25_000, 20_000],
):
    height: float = cruising_altitude - 10_000
    distance = height / math.sin(math.radians(AIRCRAFT_ASCEND_ANGLE_IN_DEGREES))
    distance = feet_to_nautical_miles(distance)


# print(calc_number_of_flyers(1_000_000, 10_000_000, 175_000_000))

if __name__ == "__main__":
    main()
