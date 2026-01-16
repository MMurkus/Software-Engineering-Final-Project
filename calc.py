#  Fetch from DB of all metro pops
# GPS coords
from geopy.distance import great_circle
from timezonefinder import TimezoneFinder
import json
import typing
import requests

PERCENT_OF_FLYERS = 0.005
MARKET_SHARE = 0.02

icao_codes = [
    "KATL",  # Atlanta
    "KDFW",  # Dallas/Fort Worth
    "KDEN",  # Denver
    "KORD",  # Chicago O'Hare
    "KLAX",  # Los Angeles
    "KJFK",  # New York JFK
    "KCLT",  # Charlotte
    "KLAS",  # Las Vegas
    "KMCO",  # Orlando
    "KMIA",  # Miami
    "KPHX",  # Phoenix
    "KSEA",  # Seattle-Tacoma
    "KSFO",  # San Francisco
    "KEWR",  # Newark
    "KIAH",  # Houston Intercontinental
    "KBOS",  # Boston Logan
    "KMSP",  # Minneapolis–Saint Paul
    "KFLL",  # Fort Lauderdale
    "KLGA",  # New York LaGuardia
    "KDTW",  # Detroit
    "KPHL",  # Philadelphia
    "KSLC",  # Salt Lake City
    "KBWI",  # Baltimore/Washington
    "KIAD",  # Washington Dulles
    "KSAN",  # San Diego
    "KDCA",  # Reagan National
    "KTPA",  # Tampa
    "KBNA",  # Nashville
    "KAUS",  # Austin
    "PHNL",  # Honolulu (note: Hawaii uses PH, not K)
]


def main():
    # print(airports["iata"])
    data = {}
    for airport in icao_codes:
        response = requests.get(
            f"https://airportdb.io/api/v1/airport/{airport}?apiToken=7c9a792f46b1b7c63b174cc811c45a6ec439e49d3ab497be5c174636b9382bc50346678f6ef0810492fa9f28ce62068c"
        )
        print(response.json())
        data[airport] = response.json()

    with open("airports.json", "w") as f:
        f.write(json.dumps(data))

    # print(airports)
    is_reachable_airport()


# Filter by reachable airports (more than 150 miles apart & operates when landing)


def is_reachable_airport():
    obj = TimezoneFinder()
    tf = TimezoneFinder(in_memory=True)
    query_points = [(13.358, 52.5061)]
    for lng, lat in query_points:
        tz = tf.timezone_at(lng=lng, lat=lat)
        print(tz)


def calc_number_of_flyers(
    source_metro_pop: float,
    dest_metro_pop: float,
    total_reachable_pop_excluding_source: float,
):
    daily_flyers = source_metro_pop * PERCENT_OF_FLYERS
    panther_flyers = daily_flyers * MARKET_SHARE

    dest_share = dest_metro_pop / total_reachable_pop_excluding_source
    return panther_flyers * dest_share


main()
# print(calc_number_of_flyers(1_000_000, 10_000_000, 175_000_000))
