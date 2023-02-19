import logging

import yagmail
from latloncalc.latlon import Latitude, Longitude

from BoatBuddy import globals

log_filename = ''


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


def get_logger():
    return logging.getLogger(globals.LOGGER_NAME)


def set_log_filename(filename):
    global log_filename
    log_filename = filename


def get_last_log_entries(count) -> []:
    lines = []

    try:
        with open(log_filename) as file:
            # loop to read iterate
            # last n lines and print it
            for line in (file.readlines()[-count:]):
                lines.append(line.rstrip('\r\n'))
    except Exception as e:
        get_logger().error(f'Could not open log file with filename {log_filename}. Details: {e}')

    return lines


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


def send_email(options, subject, body, attachments=None):
    if not options.email_module:
        return

    if options.email_address and options.email_password:
        receiver = options.email_address
        yagmail.register(options.email_address, options.email_password)
        yag = yagmail.SMTP(receiver)
        yag.send(to=receiver, subject=subject, contents=body, attachments=attachments)
    else:
        raise ValueError('Email account credentials not provided!')
