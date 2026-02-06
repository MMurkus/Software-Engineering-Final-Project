import os

# ==  CSV ROOT==
script_dir = os.path.dirname(os.path.realpath(__file__))
print(script_dir)

CSV_ROOT = f"{script_dir}/../../CSVs"
JSON_ROOT = f"{script_dir}/../../JSONs"

# == CONSTANTS ==
API_TOKEN = "7c9a792f46b1b7c63b174cc811c45a6ec439e49d3ab497be5c174636b9382bc50346678f6ef0810492fa9f28ce62068c"
PERCENT_OF_FLYERS: float = 0.005
MARKET_SHARE: float = 0.2
MIN_MILES: float = 150.0
HUBS: set[str] = set()

# == CONVERSIONS ==
KNOTS_TO_FT_PER_MIN: float = 101.27
ANGLE_OF_ASCENSION_IN_DEGREES: float = 6.00
RATE_OF_DESCEND: float = 1000 / 3
SPEED_IN_KNOTS_TO_DESCEND: float = 250
AIRCRAFT_ASCEND_ANGLE_IN_DEGREES: float = 6.00
METERS_PER_NM = 1852.0

# == TIMES & ASCEND RATES==
TURNAROUND_TIME: float = 40.0
REFUEL_TIME: float = 10.0

TIME_TO_LIFTOFF: float = 1.00

TIME_TO_10000FT: float = 4.347
DISTANCE_IN_NM_TO_10000FT: float = 15.7449

TIME_TO_ACCEL_TO_280KT: float = 1.20
DISTANCE_IN_NM_TRAVELED_WHILE_ACCEL_TO_280KT: float = 5.30

SPEED_IN_KNOTS_AT_CRUISING: float = 280.00
ACCELERATION_RATE_AT_CRUISING: float = 25.00
TIME_TO_DESCEND_TO_GROUND: float = 9.49
WESTBOUND_TIME_MULTIPLIER: float = 1.045
# TIME TO CRUSIING & DISTIANCE TO CRUSING

TIME_TO_STOP: float = 2.00
RATE_OF_ASCEND_IN_MIN_AT_280KT: float = 280 / 60

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
