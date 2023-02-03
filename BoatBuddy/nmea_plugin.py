import csv
import math
import socket
import threading
from io import StringIO

from events import Events
from geopy.geocoders import Nominatim
from latloncalc.latlon import LatLon, Latitude, Longitude

from BoatBuddy import config
from BoatBuddy import utils
from BoatBuddy.generic_plugin import GenericPlugin


class NMEAPluginEvents(Events):
    __events__ = ('on_connect', 'on_disconnect',)


class NMEAEntry:

    def __init__(self, heading, true_wind_speed, true_wind_direction,
                 apparent_wind_speed, apparent_wind_angle, gps_longitude, gps_latitude,
                 water_temperature, depth, speed_over_ground, speed_over_water,
                 distance_from_previous_entry, cumulative_distance):
        self._heading = heading
        self._true_wind_speed = true_wind_speed
        self._true_wind_direction = true_wind_direction
        self._apparent_wind_speed = apparent_wind_speed
        self._apparent_wind_angle = apparent_wind_angle
        self._gps_longitude = gps_longitude
        self._gps_latitude = gps_latitude
        self._water_temperature = water_temperature
        self._depth = depth
        self._speed_over_ground = speed_over_ground
        self._speed_over_water = speed_over_water
        self._distance_from_previous_entry = distance_from_previous_entry
        self._cumulative_distance = cumulative_distance

    def __str__(self):
        return utils.get_comma_separated_string(self.get_values())

    def get_values(self):
        lon = self._gps_longitude.to_string("d%°%m%\'%S%\" %H")
        lat = self._gps_latitude.to_string("d%°%m%\'%S%\" %H")
        return [f'{self._heading}', f'{self._true_wind_speed}',
                f'{self._true_wind_direction}', f'{self._apparent_wind_speed}', f'{self._apparent_wind_angle}', lon,
                lat,
                f'{self._water_temperature}', f'{self._depth}', f'{self._speed_over_ground}',
                f'{self._speed_over_water}', f'{self._distance_from_previous_entry}', f'{self._cumulative_distance}']

    def get_heading(self):
        return self._heading

    def get_true_wind_speed(self):
        return self._true_wind_speed

    def get_true_wind_direction(self):
        return self._true_wind_direction

    def get_apparent_wind_speed(self):
        return self._apparent_wind_speed

    def get_apparent_wind_angle(self):
        return self._apparent_wind_angle

    def get_gps_longitude(self):
        return self._gps_longitude

    def get_gps_latitude(self):
        return self._gps_latitude

    def get_water_temperature(self):
        return self._water_temperature

    def get_depth(self):
        return self._depth

    def get_speed_over_ground(self):
        return self._speed_over_ground

    def get_speed_over_water(self):
        return self._speed_over_water

    def get_distance_from_previous_entry(self):
        return self._distance_from_previous_entry

    def get_cumulative_distance(self):
        return self._cumulative_distance


class NMEAPlugin(GenericPlugin):
    _log_entries = []
    _server_ip = ''
    _server_port = 0

    _water_temperature = 0.0
    _depth = 0.0
    _heading = 0
    _gps_latitude = Latitude()
    _gps_longitude = Longitude()
    _true_wind_speed = 0
    _true_wind_direction = 0
    _apparent_wind_speed = 0.0
    _apparent_wind_angle = 0
    _speed_over_water = 0.0
    _speed_over_ground = 0.0

    _exit_signal = threading.Event()
    _nmea_server_thread = threading.Thread()
    _events = None

    def __init__(self, args):
        # invoking the __init__ of the parent class
        GenericPlugin.__init__(self, args)

        self._server_ip = args.nmea_server_ip
        self._server_port = int(args.nmea_port)
        self._exit_signal = threading.Event()
        self._nmea_server_thread = threading.Thread(target=self._run_client)
        self._nmea_server_thread.start()

    def get_metadata_headers(self):
        return ["True Heading (degrees)", "True Wind Speed (knots)",
                "True Wind Direction (degrees)", "Apparent Wind Speed (knots)",
                "Apparent Wind Angle (Relative degrees)", "GPS Longitude (d°m\'S\" H)",
                "GPS Latitude (d°m\'S\" H)", "Water Temperature (°C)",
                "Depth (meters)", "Speed Over Ground (knots)", "Speed Over Water (knots)",
                "Distance From Previous Entry (miles)", "Cumulative Distance (miles)"]

    def take_snapshot(self):
        # Calculate the distance traveled so far and the distance from the last recorded entry
        cumulative_distance = 0.0
        distance_from_previous_entry = 0.0
        entries_count = len(self._log_entries)
        if self._gps_latitude and self._gps_longitude and entries_count > 0:
            latlon_start = LatLon(self._log_entries[entries_count - 1].get_gps_latitude(),
                                  self._log_entries[entries_count - 1].get_gps_longitude())
            latlon_end = LatLon(self._gps_latitude, self._gps_longitude)
            distance_from_previous_entry = round(float(latlon_end.distance(latlon_start) / 1.852), 1)
            cumulative_distance = round(float(self._log_entries[entries_count - 1].get_cumulative_distance())
                                        + distance_from_previous_entry, 1)

        # Create a new entry
        entry = NMEAEntry(self._heading, self._true_wind_speed, self._true_wind_direction,
                          self._apparent_wind_speed, self._apparent_wind_angle, self._gps_longitude, self._gps_latitude,
                          self._water_temperature, self._depth, self._speed_over_ground, self._speed_over_water,
                          distance_from_previous_entry, cumulative_distance)

        # Add it to the list of entries in memory
        self._log_entries.append(entry)

    def get_metadata_values(self):
        # Return last entry values
        return self._log_entries[len(self._log_entries) - 1].get_values()

    def get_summary_headers(self):
        return ["Starting Location (City, Country)",
                "Ending Location (City, Country)", "Starting GPS Latitude (d°m\'S\" H)",
                "Starting GPS Longitude (d°m\'S\" H)", "Ending GPS Latitude (d°m\'S\" H)",
                "Ending GPS Longitude (d°m\'S\" H)", "Distance (miles)", "Heading (degrees)",
                "Average Wind Speed (knots)", "Average Wind Direction (degrees)",
                "Average Water Temperature (°C)", "Average Depth (meters)",
                "Average Speed Over Ground (knots)", "Average Speed Over Water (knots)"]

    def get_summary_values(self):
        log_summary_list = []

        if len(self._log_entries) > 0:
            first_entry = self._log_entries[0]
            last_entry = self._log_entries[len(self._log_entries) - 1]

            # Try to fetch the starting and ending location cities
            geolocator = Nominatim(user_agent="geoapiExercises")
            starting_location = geolocator.reverse(f'{first_entry.get_gps_latitude()}' + ',' +
                                                   f'{first_entry.get_gps_longitude()}')
            starting_location_str = starting_location.raw['address'].get('city', '') + ', ' + \
                                    starting_location.raw['address'].get('country', '')
            log_summary_list.append(starting_location_str)

            ending_location = geolocator.reverse(f'{last_entry.get_gps_latitude()}' + ',' +
                                                 f'{last_entry.get_gps_longitude()}')
            ending_location_str = ending_location.raw['address'].get('city', '') + ', ' + \
                                  ending_location.raw['address'].get('country', '')
            log_summary_list.append(ending_location_str)

            # Collect GPS coordinates
            log_summary_list.append(first_entry.get_gps_latitude().to_string("d%°%m%\'%S%\" %H"))
            log_summary_list.append(first_entry.get_gps_longitude().to_string("d%°%m%\'%S%\" %H"))
            log_summary_list.append(last_entry.get_gps_latitude().to_string("d%°%m%\'%S%\" %H"))
            log_summary_list.append(last_entry.get_gps_longitude().to_string("d%°%m%\'%S%\" %H"))

            # Calculate travelled distance and heading
            latlon_start = LatLon(first_entry.get_gps_latitude(), first_entry.get_gps_longitude())
            latlon_end = LatLon(last_entry.get_gps_latitude(), last_entry.get_gps_longitude())
            distance = round(float(latlon_end.distance(latlon_start) / 1.852), 2)
            log_summary_list.append(distance)
            heading = math.floor(float(latlon_end.heading_initial(latlon_start)))
            log_summary_list.append(heading)

            # Calculate averages
            sum_wind_speed = 0
            sum_true_wind_direction = 0
            sum_water_temperature = 0
            sum_depth = 0
            sum_speed_over_ground = 0
            sum_speed_over_water = 0
            count = len(self._log_entries)
            for entry in self._log_entries:
                sum_wind_speed += float(entry.get_true_wind_speed())
                sum_true_wind_direction += int(entry.get_true_wind_direction())
                sum_water_temperature += float(entry.get_water_temperature())
                sum_depth += float(entry.get_depth())
                sum_speed_over_ground += float(entry.get_speed_over_ground())
                sum_speed_over_water += float(entry.get_speed_over_water())

            log_summary_list.append(round(sum_wind_speed / count))
            log_summary_list.append(int(sum_true_wind_direction / count))
            log_summary_list.append(round(sum_water_temperature / count, 1))
            log_summary_list.append(round(sum_depth / count, 1))
            log_summary_list.append(round(sum_speed_over_ground / count, 1))
            log_summary_list.append(round(sum_speed_over_water / count, 1))

        return log_summary_list

    def reset_entries(self):
        self._log_entries = []

    def _run_client(self):
        while not self._exit_signal.is_set():
            utils.get_logger().info(f'Trying to connect to NMEA0183 server with address {self._server_ip} on ' +
                                    f'port {self._server_port}...')
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(config.SOCKET_TIMEOUT)

            try:
                client.connect((self._server_ip, self._server_port))

                utils.get_logger().info(f'Connection to NMEA0183 server established')

                if self._events:
                    self._events.on_connect()

                while not self._exit_signal.is_set():
                    data = client.recv(config.BUFFER_SIZE)
                    if data is None:
                        utils.get_logger().info('No NMEA0183 data received')
                        break

                    str_data = data.decode().rstrip('\r\n')
                    utils.get_logger().debug(str_data)
                    self._process_data(str_data)

            except TimeoutError:
                utils.get_logger().info(f'Connection to server {self._server_ip} is lost!')
            except OSError:
                utils.get_logger().info(f'Server {self._server_ip} is down!')
            finally:
                client.close()
                if self._exit_signal.is_set():
                    utils.get_logger().info('NMEA plugin instance is ready to be destroyed')
                elif self._events:
                    self._events.on_disconnect()

    def _process_data(self, payload):
        if payload is None:
            return

        buff = StringIO(payload)
        csv_reader = csv.reader(buff)
        csv_list = list(csv_reader)[0]
        str_csv_list_type = csv_list[0]

        # Determine the type of data
        if str_csv_list_type == "$IIHDG":
            if csv_list[1] != '':
                self._heading = math.floor(float(csv_list[1]))
                utils.get_logger().info(f'Detected heading {self._heading} degrees (True north)')
        elif str_csv_list_type == "$GPGPU":
            if csv_list[2] != '' and csv_list[3] != '' and csv_list[4] != '' and csv_list[5] != '':
                self._gps_latitude = utils.get_latitude(csv_list[2], csv_list[3])
                self._gps_longitude = utils.get_longitude(csv_list[4], csv_list[5])
                utils.get_logger().debug(
                    f'Detected GPS coordinates Latitude: {self._gps_latitude} Longitude: {self._gps_longitude}')
        elif str_csv_list_type == "$SDMTW":
            if csv_list[1] != '':
                self._water_temperature = float(csv_list[1])
                utils.get_logger().debug(f'Detected Temperature {self._water_temperature} Celsius')
        elif str_csv_list_type == "$SDDPT":
            if csv_list[1] != '':
                if csv_list[2] != '':
                    self._depth = float(csv_list[1]) + float(csv_list[2])
                else:
                    self._depth = float(csv_list[1])
                self._depth = int(self._depth * 10) / 10
                utils.get_logger().debug(f'Detected depth {self._depth} meters')
        elif str_csv_list_type == "$GPVTG":
            if csv_list[5] != '':
                self._speed_over_ground = csv_list[5]
                utils.get_logger().debug(f'Detected speed over ground {self._speed_over_ground} knots')
        elif str_csv_list_type == "$WIMWD":
            if csv_list[1] != '' and csv_list[5] != '':
                self._true_wind_direction = math.floor(float(csv_list[1]))
                self._true_wind_speed = csv_list[5]
                utils.get_logger().debug(
                    f'Detected true wind direction {self._true_wind_direction} degrees (True north) ' +
                    f'and speed {self._true_wind_speed} knots')
        elif str_csv_list_type == "$WIMWV":
            if csv_list[1] != '' and csv_list[3] != '':
                if self._true_wind_direction != "":
                    self._apparent_wind_angle = math.floor(float(csv_list[1]))
                self._apparent_wind_speed = csv_list[3]
                utils.get_logger().debug(
                    f'Detected apparent wind angle {self._apparent_wind_angle} degrees and ' +
                    f'speed {self._apparent_wind_speed} knots')
        elif str_csv_list_type == "$SDVHW":
            if csv_list[5] != '':
                self._speed_over_water = csv_list[5]
                utils.get_logger().debug(f'Detected speed over water {self._speed_over_water} knots')

    def get_last_latitude_entry(self):
        if len(self._log_entries) > 0:
            return self._log_entries[len(self._log_entries) - 1].get_gps_latitude()
        else:
            return self._gps_latitude

    def get_last_longitude_entry(self):
        if len(self._log_entries) > 0:
            return self._log_entries[len(self._log_entries) - 1].get_gps_longitude()
        else:
            return self._gps_longitude

    def finalize(self):
        self._exit_signal.set()
        utils.get_logger().info("NMEA plugin worker thread notified...")

    def register_for_events(self, events):
        self._events = events
