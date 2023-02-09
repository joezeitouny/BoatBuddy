import logging

from latloncalc.latlon import Latitude, Longitude

from BoatBuddy import config

log_filename = ''


def get_application_version():
    return config.APPLICATION_VERSION


def get_application_name():
    return config.APPLICATION_NAME


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


def get_logger():
    return logging.getLogger(config.LOGGER_NAME)


def set_log_filename(filename):
    global log_filename
    log_filename = filename


def get_last_log_entries(count) -> []:
    lines = []
    with open(log_filename) as file:
        # loop to read iterate
        # last n lines and print it
        for line in (file.readlines()[-count:]):
            lines.append(line.rstrip('\r\n'))

    return lines


def get_key_value_list(keys, values) -> {}:
    if not keys or not values:
        return {}

    key_value_list = {}
    counter = 0
    for key in keys:
        key_value_list[key] = values[counter]
        counter += 1
    return key_value_list


def get_filtered_key_value_list(original_key_value_list, filter_list) -> {}:
    if not original_key_value_list or not filter_list:
        return {}

    key_value_list = {}
    for key in filter_list:
        key_value_list[key] = original_key_value_list[key]
    return key_value_list


def get_comma_separated_string(values_list):
    if len(values_list) == 0:
        return ''
    elif len(values_list) == 1:
        return values_list[0]
    else:
        comma_separated_list = ''
        for entry in values_list:
            comma_separated_list = comma_separated_list + f'{entry},'

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
    return (0.1 * float(coord_str.split('.')[1]) * 60) / 1000


def get_latitude(coord_str, hemispehere):
    lat = Latitude(get_degrees(coord_str), get_minutes(coord_str),
                   get_seconds(coord_str))
    lat.set_hemisphere(hemispehere)
    return lat


def get_longitude(coord_str, hemispehere):
    lon = Longitude(get_degrees(coord_str), get_minutes(coord_str),
                    get_seconds(coord_str))
    lon.set_hemisphere(hemispehere)
    return lon


def get_biggest_number(number1, number2):
    if number1 > number2:
        return number1
    return number2


def get_smallest_number(number1, number2):
    if number1 < number2:
        return number1
    return number2
