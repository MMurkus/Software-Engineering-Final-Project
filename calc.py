import json
import csv
import os
from typing import Union
import requests
from datetime import datetime
import zoneinfo
from geopy.distance import great_circle  # type: ignore

# import requests
API_TOKEN = "7c9a792f46b1b7c63b174cc811c45a6ec439e49d3ab497be5c174636b9382bc50346678f6ef0810492fa9f28ce62068c"

PERCENT_OF_FLYERS: float = 0.005
MARKET_SHARE: float = 0.5
MIN_MILES: float = 150.0

icao_to_timezone = {
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


def main():
    airports = None
    if os.path.isfile("./airports.json"):
        with open("airports.json", "r") as f:
            airports = json.load(f)
    else:
        with open("airports.json", "w") as f:
            airports = fetch_airports(list(icao_to_timezone.keys()))

    calculate_distances(airports)

    for key in icao_to_timezone.values():
        get_time_of_city(key)


def calculate_distances(airports: dict) -> None:
    distances: dict = {}
    airport_coords: list[tuple] = []

    for airport, airport_data in airports.items():
        icao, latitude, longitude = (
            airport,
            airport_data.get("latitude_deg"),
            airport_data.get("longitude_deg"),
        )

        if not airport_data or not longitude:
            raise ValueError(f"[-] Unable fetch GPS data for {airport}")

        airport_coords.append((icao, latitude, longitude))

    with open(
        "distances.csv",
        "w",
    ) as f:
        writer = csv.writer(f)
        writer.writerow([""] + list(icao_to_timezone.keys()))

        for source_airport, *source_airport_coords in airport_coords:
            row: list[Union[float, str]] = []
            for dest_airport, *dest_airport_coords in airport_coords:
                if source_airport == dest_airport:
                    row.append(0.00)
                    continue

                miles: float = great_circle(
                    source_airport_coords, dest_airport_coords
                ).miles

                row.append(round(miles, 5) if miles >= MIN_MILES else "LESS_THAN_150")

            distances[source_airport] = row
            writer.writerow([source_airport] + row)


def is_reachable_airport(source_coords: tuple, destination_coords): ...


"""
Format of timezone expected : "America/New_York" | "Europe/Paris"
"""


def get_time_of_city(iana_time_zone: str) -> datetime:
    local_timezone = zoneinfo.ZoneInfo(iana_time_zone)
    local_time = datetime.now(local_timezone)
    print(f"Time in ({iana_time_zone.split('\/')[-1]}) : ", end="")
    print(
        local_time.strftime("%Y-%m-%d %H:%M:%S ")
    )  # Could add %Z timezone zone (e.g UTC,EST), %z outputs the UTC Offset
    return local_time


def calc_number_of_flyers(
    source_metro_pop: float,
    dest_metro_pop: float,
    total_reachable_pop_excluding_source: float,
):
    daily_flyers = source_metro_pop * PERCENT_OF_FLYERS
    panther_flyers = daily_flyers * MARKET_SHARE

    dest_share = dest_metro_pop / total_reachable_pop_excluding_source
    return panther_flyers * dest_share


def fetch_airports(icao_to_timezone: list[str]) -> dict:
    data = {}
    for icao in icao_to_timezone:
        url = f"https://airportdb.io/api/v1/airport/{icao}?apiToken={API_TOKEN}"
        print(f"[+] Fetching {icao} ({url})")
        request = requests.get(url, timeout=30)
        data[icao] = request.json()

    with open("airports.json", "w") as f:
        f.write(json.dumps(data))
    return data


main()
# print(calc_number_of_flyers(1_000_000, 10_000_000, 175_000_000))

if __name__ == "__main__":
    main()
