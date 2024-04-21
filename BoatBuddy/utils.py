from enum import Enum
import math
import os

from latloncalc.latlon import Latitude, Longitude

from BoatBuddy import globals


class ModuleStatus(Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'
    ALARM_ACTIVE = 'alarm_active'  # used in the anchor alarm module
    ALARM_CLEARED = 'alarm_cleared'  # used in the anchor alarm module


def get_application_version():
    return globals.APPLICATION_VERSION


def get_application_name():
    return globals.APPLICATION_NAME


def try_parse_bool(value) -> bool:
    if not value:
        return False

    result = False
    try:
        if str(value).upper() == 'TRUE':
            result = True
    except Exception:
        pass

    return result


def try_parse_int(value) -> int:
    if not value:
        return 0

    result = 0
    try:
        result = int(value)
    except ValueError:
        pass
    return result


def try_parse_float(value) -> float:
    if not value:
        return 0.0

    result = 0.0
    try:
        result = float(value)
    except ValueError:
        pass
    return result


def get_colour_for_key_value_in_dictionary(collection: dict, key: str, value: float) -> str:
    colour_result = 'default'

    if key in collection.keys():
        configuration = collection[key]
        for colour_key in configuration:
            if configuration[colour_key][1] >= try_parse_float(value) > configuration[colour_key][0]:
                colour_result = colour_key
                break

    return colour_result


def get_key_value_list(keys, values) -> {}:
    if not keys or not values:
        return {}

    key_value_list = {}
    counter = 0
    for key in keys:
        key_value_list[key] = str(values[counter])
        counter += 1
    return key_value_list


def get_filtered_key_value_list(original_key_value_list, filter_list) -> {}:
    if not original_key_value_list or not filter_list:
        return {}

    key_value_list = {}
    for key in filter_list:
        key_value_list[key] = str(original_key_value_list[key])
    return key_value_list


def get_comma_separated_string(values_list):
    if len(values_list) == 0:
        return ''
    elif len(values_list) == 1:
        return values_list[0]
    else:
        comma_separated_list = ''
        for entry in values_list:
            comma_separated_list = comma_separated_list + f'"{entry}",'

        return comma_separated_list[:-1]


def get_degrees(coord_str):
    if len(coord_str.split('.')[0]) == 5:
        # We're dealing with negative coordinates here
        return float(coord_str[1:3])
    else:
        return float(coord_str[:2])


def get_minutes(coord_str):
    return float(coord_str.split('.')[0][-2:])


def get_seconds(coord_str):
    if len(coord_str.split('.')[1]) == 5:
        return round((0.1 * int(coord_str.split('.')[1]) * 60) / 10000, 2)
    else:
        return round((0.1 * int(coord_str.split('.')[1]) * 60) / 1000, 2)


def get_latitude(coord_str, hemisphere):
    lat = Latitude(get_degrees(coord_str), get_minutes(coord_str),
                   get_seconds(coord_str))
    lat.set_hemisphere(hemisphere)
    return lat


def get_str_from_latitude(latitude):
    return latitude.to_string("d%°%m%\'%S%").rstrip('0') + latitude.to_string("\" %H")


def get_str_from_longitude(longitude):
    return longitude.to_string("d%°%m%\'%S%").rstrip('0') + longitude.to_string("\" %H")


def get_longitude(coord_str, hemisphere):
    lon = Longitude(get_degrees(coord_str), get_minutes(coord_str),
                    get_seconds(coord_str))
    lon.set_hemisphere(hemisphere)
    return lon


def get_biggest_number(number1, number2):
    if number1 > number2:
        return number1
    return number2


def get_smallest_number(number1, number2):
    if number1 < number2:
        return number1
    return number2


def dms_to_dd(degrees, minutes, seconds, direction):
    # Convert DMS to DD
    dd = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)
    if direction in ['S', 'W']:
        dd *= -1  # Apply negative sign for South and West directions
    return dd


def calculate_bearing(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Calculate the bearing using the Haversine formula
    delta_lon = lon2 - lon1

    y = math.sin(delta_lon)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)

    bearing = math.atan2(y, x)

    # Convert the bearing from radians to degrees
    bearing = math.degrees(bearing)

    # Normalize the initial bearing to the range [0, 360]
    bearing = (bearing + 360) % 360

    # round it
    bearing = round(bearing)

    return bearing


def calculate_destination_point(lat1, lon1, bearing, distance):
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    bearing = math.radians(bearing)

    # Calculate the destination point's latitude
    lat2 = math.asin(math.sin(lat1) * math.cos(distance / globals.EARTH_RADIUS) +
                     math.cos(lat1) * math.sin(distance / globals.EARTH_RADIUS) * math.cos(bearing))

    # Calculate the destination point's longitude
    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance / globals.EARTH_RADIUS) * math.cos(lat1),
                             math.cos(distance / globals.EARTH_RADIUS) - math.sin(lat1) * math.sin(lat2))

    # Convert the latitude and longitude back to degrees
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)

    return lat2, lon2


def file_exists(file_path):
    try:
        if os.path.exists(file_path):
            return True

        return False
    except Exception as e:
        return False


def directory_exists(path):
    try:
        return os.path.exists(path) and os.path.isdir(path)
    except Exception as e:
        return False
