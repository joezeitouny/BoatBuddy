import logging

from latloncalc.latlon import Latitude, Longitude

from BoatBuddy import config


def get_logger():
    return logging.getLogger(config.LOGGER_NAME)


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
