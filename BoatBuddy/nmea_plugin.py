import csv
import math
import socket
import threading
import time
from io import StringIO

from events import Events
from geopy.geocoders import Nominatim
from latloncalc.latlon import LatLon, Latitude, Longitude, string2latlon

from BoatBuddy import globals, utils
from BoatBuddy.generic_plugin import GenericPlugin, PluginStatus


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
        lat = globals.EMPTY_METRIC_VALUE
        lon = globals.EMPTY_METRIC_VALUE
        if not isinstance(self._gps_latitude, str):
            lat = utils.get_str_from_latitude(self._gps_latitude)
        if not isinstance(self._gps_longitude, str):
            lon = utils.get_str_from_longitude(self._gps_longitude)
        return [f'{self._heading}', f'{self._true_wind_speed}',
                f'{self._true_wind_direction}', f'{self._apparent_wind_speed}', f'{self._apparent_wind_angle}', lat,
                lon,
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

    def __init__(self, options, log_manager):
        # invoking the __init__ of the parent class
        GenericPlugin.__init__(self, options, log_manager)

        # Instance metrics
        self._water_temperature = globals.EMPTY_METRIC_VALUE
        self._depth = globals.EMPTY_METRIC_VALUE
        self._heading = globals.EMPTY_METRIC_VALUE
        self._gps_latitude = globals.EMPTY_METRIC_VALUE
        self._gps_longitude = globals.EMPTY_METRIC_VALUE
        self._true_wind_speed = globals.EMPTY_METRIC_VALUE
        self._true_wind_direction = globals.EMPTY_METRIC_VALUE
        self._apparent_wind_speed = globals.EMPTY_METRIC_VALUE
        self._apparent_wind_angle = globals.EMPTY_METRIC_VALUE
        self._speed_over_water = globals.EMPTY_METRIC_VALUE
        self._speed_over_ground = globals.EMPTY_METRIC_VALUE
        self._gps_fix_captured = False
        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]
        self._sum_wind_speed = 0
        self._cnt_wind_speed_entries = 0
        self._sum_true_wind_direction = 0
        self._cnt_true_wind_direction_entries = 0
        self._sum_water_temperature = 0
        self._cnt_water_temperature_entries = 0
        self._sum_depth = 0
        self._cnt_depth_entries = 0
        self._sum_speed_over_ground = 0
        self._cnt_speed_over_ground_entries = 0
        self._sum_speed_over_water = 0
        self._cnt_speed_over_water_entries = 0

        # Other instance variables
        self._plugin_status = PluginStatus.STARTING
        self._server_ip = options.nmea_server_ip
        self._server_port = options.nmea_server_port
        self._events = None
        self._process_data_thread = threading.Thread()
        self._exit_signal = threading.Event()
        self._timer = threading.Timer(1, self.connect_to_server)
        self._timer.start()
        self._log_manager.info('NMEA0183 module successfully started!')

    def reset_instance_metrics(self):
        self._water_temperature = globals.EMPTY_METRIC_VALUE
        self._depth = globals.EMPTY_METRIC_VALUE
        self._heading = globals.EMPTY_METRIC_VALUE
        self._gps_latitude = globals.EMPTY_METRIC_VALUE
        self._gps_longitude = globals.EMPTY_METRIC_VALUE
        self._true_wind_speed = globals.EMPTY_METRIC_VALUE
        self._true_wind_direction = globals.EMPTY_METRIC_VALUE
        self._apparent_wind_speed = globals.EMPTY_METRIC_VALUE
        self._apparent_wind_angle = globals.EMPTY_METRIC_VALUE
        self._speed_over_water = globals.EMPTY_METRIC_VALUE
        self._speed_over_ground = globals.EMPTY_METRIC_VALUE
        self._gps_fix_captured = False
        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]
        self._sum_wind_speed = 0
        self._cnt_wind_speed_entries = 0
        self._sum_true_wind_direction = 0
        self._cnt_true_wind_direction_entries = 0
        self._sum_water_temperature = 0
        self._cnt_water_temperature_entries = 0
        self._sum_depth = 0
        self._cnt_depth_entries = 0
        self._sum_speed_over_ground = 0
        self._cnt_speed_over_ground_entries = 0
        self._sum_speed_over_water = 0
        self._cnt_speed_over_water_entries = 0

    def get_metadata_headers(self):
        return globals.NMEA_PLUGIN_METADATA_HEADERS.copy()

    def take_snapshot(self, store_entry):
        # Calculate the distance traveled so far and the distance from the last recorded entry
        cumulative_distance = globals.EMPTY_METRIC_VALUE
        distance_from_previous_entry = globals.EMPTY_METRIC_VALUE
        entries_count = len(self._log_entries)
        # Check first if we currently have a GPS fix and that there is at least one previously logged entry
        if self.is_gps_fix_captured() and entries_count > 0 and \
                self._log_entries[entries_count - 1].get_gps_latitude() != globals.EMPTY_METRIC_VALUE and \
                self._log_entries[entries_count - 1].get_gps_longitude() != globals.EMPTY_METRIC_VALUE and \
                self._gps_latitude != globals.EMPTY_METRIC_VALUE and self._gps_longitude != globals.EMPTY_METRIC_VALUE:
            latlon_start = LatLon(self._log_entries[entries_count - 1].get_gps_latitude(),
                                  self._log_entries[entries_count - 1].get_gps_longitude())
            # Only calculate the distance and cumulative distance metrics if the last entry has a valid GPS fix
            if latlon_start.to_string() != LatLon(Latitude(), Longitude()).to_string():
                latlon_end = LatLon(self._gps_latitude, self._gps_longitude)
                distance_from_previous_entry = round(float(latlon_end.distance(latlon_start) / 1.852), 1)
                if self._log_entries[entries_count - 1].get_cumulative_distance() == globals.EMPTY_METRIC_VALUE:
                    cumulative_distance = round(distance_from_previous_entry, 1)
                else:
                    cumulative_distance = round(float(self._log_entries[entries_count - 1].get_cumulative_distance())
                                                + distance_from_previous_entry, 1)

        # Create a new entry
        entry = NMEAEntry(self._heading, self._true_wind_speed, self._true_wind_direction,
                          self._apparent_wind_speed, self._apparent_wind_angle, self._gps_longitude, self._gps_latitude,
                          self._water_temperature, self._depth, self._speed_over_ground, self._speed_over_water,
                          distance_from_previous_entry, cumulative_distance)

        # Add it to the list of entries in memory
        if store_entry:
            self._log_entries.append(entry)

            # Collect the GPS coordinates from the first entry which has valid ones
            if self._summary_values[2] == globals.EMPTY_METRIC_VALUE and \
                    self._summary_values[3] == globals.EMPTY_METRIC_VALUE and \
                    entry.get_gps_latitude() != globals.EMPTY_METRIC_VALUE and \
                    entry.get_gps_longitude() != globals.EMPTY_METRIC_VALUE:
                self._summary_values[2] = utils.get_str_from_latitude(entry.get_gps_latitude())
                self._summary_values[3] = utils.get_str_from_longitude(entry.get_gps_longitude())

            # Collect the GPS coordinates from the last entry which has valid ones
            if entry.get_gps_latitude() != globals.EMPTY_METRIC_VALUE and \
                    entry.get_gps_longitude() != globals.EMPTY_METRIC_VALUE:
                self._summary_values[4] = utils.get_str_from_latitude(entry.get_gps_latitude())
                self._summary_values[5] = utils.get_str_from_longitude(entry.get_gps_longitude())

            if self._summary_values[2] != globals.EMPTY_METRIC_VALUE and \
                    self._summary_values[3] != globals.EMPTY_METRIC_VALUE and \
                    self._summary_values[4] != globals.EMPTY_METRIC_VALUE and \
                    self._summary_values[5] != globals.EMPTY_METRIC_VALUE:
                # Calculate travelled distance and heading
                latlon_start = string2latlon(self._summary_values[2], self._summary_values[3], 'd%°%m%\'%S%\" %H')
                latlon_end = string2latlon(self._summary_values[4], self._summary_values[5], 'd%°%m%\'%S%\" %H')
                if latlon_start.to_string("D") != latlon_end.to_string("D"):
                    distance = round(float(latlon_end.distance(latlon_start) / 1.852), 2)
                    self._summary_values[6] = distance
                    heading = math.floor(float(latlon_end.heading_initial(latlon_start)))
                    self._summary_values[7] = heading

            # Calculate averages
            if entry.get_true_wind_speed() != globals.EMPTY_METRIC_VALUE:
                self._sum_wind_speed += utils.try_parse_float(entry.get_true_wind_speed())
                self._cnt_wind_speed_entries += 1
                if self._summary_values[8] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[8] = entry.get_true_wind_speed()
                else:
                    self._summary_values[8] = round(self._sum_wind_speed / self._cnt_wind_speed_entries)

            if entry.get_true_wind_direction() != globals.EMPTY_METRIC_VALUE:
                self._sum_true_wind_direction += utils.try_parse_int(entry.get_true_wind_direction())
                self._cnt_true_wind_direction_entries += 1
                if self._summary_values[9] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[9] = entry.get_true_wind_direction()
                else:
                    self._summary_values[9] = int(self._sum_true_wind_direction / self._cnt_true_wind_direction_entries)

            if entry.get_water_temperature() != globals.EMPTY_METRIC_VALUE:
                self._sum_water_temperature += utils.try_parse_float(entry.get_water_temperature())
                self._cnt_water_temperature_entries += 1
                if self._summary_values[10] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[10] = entry.get_water_temperature()
                else:
                    self._summary_values[10] = \
                        round(self._sum_water_temperature / self._cnt_water_temperature_entries, 1)

            if entry.get_depth() != globals.EMPTY_METRIC_VALUE:
                self._sum_depth += utils.try_parse_float(entry.get_depth())
                self._cnt_depth_entries += 1
                if self._summary_values[11] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[11] = entry.get_depth()
                else:
                    self._summary_values[11] = round(self._sum_depth / self._cnt_depth_entries, 1)

            if entry.get_speed_over_ground() != globals.EMPTY_METRIC_VALUE:
                self._sum_speed_over_ground += utils.try_parse_float(entry.get_speed_over_ground())
                self._cnt_speed_over_ground_entries += 1
                if self._summary_values[12] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[12] = entry.get_speed_over_ground()
                else:
                    self._summary_values[12] = \
                        round(self._sum_speed_over_ground / self._cnt_speed_over_ground_entries, 1)

            if entry.get_speed_over_water() != globals.EMPTY_METRIC_VALUE:
                self._sum_speed_over_water += utils.try_parse_float(entry.get_speed_over_water())
                self._cnt_speed_over_water_entries += 1
                if self._summary_values[13] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[13] = entry.get_speed_over_water()
                else:
                    self._summary_values[13] = round(self._sum_speed_over_water / self._cnt_speed_over_water_entries, 1)

        return entry

    def get_metadata_values(self):
        # Return last entry values
        return self._log_entries[len(self._log_entries) - 1].get_values()

    def get_summary_headers(self):
        return globals.NMEA_PLUGIN_SUMMARY_HEADERS.copy()

    def get_summary_values(self, reverse_lookup_locations=False):
        if reverse_lookup_locations:
            geolocator = Nominatim(user_agent="BoatBuddy")
            if self._summary_values[2] != globals.EMPTY_METRIC_VALUE and \
                    self._summary_values[3] != globals.EMPTY_METRIC_VALUE:
                # Try to fetch the starting and ending location cities
                try:
                    starting_location = geolocator.reverse(f'{self._summary_values[2]}' + ',' +
                                                           f'{self._summary_values[3]}')
                    starting_location_str = \
                        starting_location.raw['address'].get('city', '') + ', ' + \
                        starting_location.raw['address'].get('country', '')
                    self._summary_values[0] = starting_location_str
                except Exception as e:
                    self._log_manager.debug(f'Could not get start location from GPS coordinates. Details: {e}')

            if self._summary_values[4] != globals.EMPTY_METRIC_VALUE and \
                    self._summary_values[5] != globals.EMPTY_METRIC_VALUE:
                try:
                    ending_location = geolocator.reverse(f'{self._summary_values[4]}' + ',' +
                                                         f'{self._summary_values[5]}')
                    ending_location_str = ending_location.raw['address'].get('city', '') + ', ' + ending_location.raw[
                        'address'].get('country', '')
                    self._summary_values[1] = ending_location_str
                except Exception as e:
                    self._log_manager.debug(f'Could not get end location from GPS coordinates. Details: {e}')

        return self._summary_values.copy()

    def connect_to_server(self):
        if self._exit_signal.is_set():
            self._plugin_status = PluginStatus.DOWN
            self._log_manager.info('NMEA plugin instance is ready to be destroyed')
            return

        self._log_manager.debug(f'Trying to connect to NMEA0183 server with address {self._server_ip} on ' +
                                f'port {self._server_port}...')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(globals.NMEA_PLUGIN_SOCKET_TIMEOUT)

        try:
            client.connect((self._server_ip, self._server_port))

            # Close the client connection
            client.close()

            # Start receiving and processing data
            self._process_data_thread = threading.Thread(target=self._process_data_loop)
            self._process_data_thread.start()
        except Exception as e:
            self._handle_connection_exception(e)

    def _process_data_loop(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(globals.NMEA_PLUGIN_SOCKET_TIMEOUT)

        try:
            client.connect((self._server_ip, self._server_port))

            while not self._exit_signal.is_set():
                data = client.recv(globals.NMEA_PLUGIN_BUFFER_SIZE)
                if data is None:
                    raise ValueError('No NMEA0183 data received')

                if self._plugin_status != PluginStatus.RUNNING:
                    self._log_manager.info(f'Connection to NMEA0183 server established')
                    self._plugin_status = PluginStatus.RUNNING

                    self.reset_instance_metrics()

                    if self._events:
                        self._events.on_connect()

                str_data = data.decode().rstrip('\r\n')
                self._log_manager.debug(str_data)
                self._process_data(str_data)

                # sleep for 1 second
                time.sleep(globals.NMEA_PLUGIN_SAMPLING_RATE)
        except Exception as e:
            self._handle_connection_exception(e)

        # Close the client connection (if any)
        client.close()

    def _handle_connection_exception(self, message):
        if self._plugin_status != PluginStatus.DOWN:
            self._log_manager.info(f'NMEA0183 Server on {self._server_ip} is down. Details: {message}')

            self._plugin_status = PluginStatus.DOWN

            # If anyone is listening to events then notify of a disconnection
            if self._events:
                self._events.on_disconnect()

        # Restart the main timer if the connection is lost
        self._timer = threading.Timer(globals.NMEA_TIMER_INTERVAL, self.connect_to_server)
        self._timer.start()

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
                self._log_manager.debug(f'Detected heading {self._heading} degrees (True north)')
        elif str_csv_list_type == "$GPGGA":
            if csv_list[6] == '1' or csv_list[6] == '2':
                self._gps_latitude = utils.get_latitude(csv_list[2], csv_list[3])
                self._gps_longitude = utils.get_longitude(csv_list[4], csv_list[5])
                self._gps_fix_captured = True
                self._log_manager.debug(
                    f'Detected GPS coordinates Latitude: {self._gps_latitude} Longitude: {self._gps_longitude}')
        elif str_csv_list_type == "$SDMTW":
            if csv_list[1] != '':
                self._water_temperature = float(csv_list[1])
                self._log_manager.debug(f'Detected Temperature {self._water_temperature} Celsius')
        elif str_csv_list_type == "$SDDPT":
            if csv_list[1] != '':
                if csv_list[2] != '':
                    self._depth = float(csv_list[1]) + float(csv_list[2])
                else:
                    self._depth = float(csv_list[1])
                self._depth = int(self._depth * 10) / 10
                self._log_manager.debug(f'Detected depth {self._depth} meters')
        elif str_csv_list_type == "$GPVTG":
            if csv_list[5] != '':
                self._speed_over_ground = csv_list[5]
                self._log_manager.debug(f'Detected speed over ground {self._speed_over_ground} knots')
        elif str_csv_list_type == "$WIMWD":
            if csv_list[1] != '' and csv_list[5] != '':
                self._true_wind_direction = math.floor(float(csv_list[1]))
                self._true_wind_speed = csv_list[5]
                self._log_manager.debug(
                    f'Detected true wind direction {self._true_wind_direction} degrees (True north) ' +
                    f'and speed {self._true_wind_speed} knots')
        elif str_csv_list_type == "$WIMWV":
            if csv_list[1] != '' and csv_list[3] != '':
                self._apparent_wind_angle = math.floor(float(csv_list[1]))
                if self._apparent_wind_angle > 180:
                    self._apparent_wind_angle = (360 - self._apparent_wind_angle) * -1
                self._apparent_wind_speed = csv_list[3]
                self._log_manager.debug(
                    f'Detected apparent wind angle {self._apparent_wind_angle} degrees and ' +
                    f'speed {self._apparent_wind_speed} knots')
        elif str_csv_list_type == "$SDVHW":
            if csv_list[5] != '':
                self._speed_over_water = csv_list[5]
                self._log_manager.debug(f'Detected speed over water {self._speed_over_water} knots')

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

    def is_gps_fix_captured(self):
        return self._gps_fix_captured

    def finalize(self):
        self._exit_signal.set()
        if self._timer:
            self._timer.cancel()
        self._log_manager.info("NMEA plugin worker thread notified...")

    def register_for_events(self, events):
        self._events = events

    def get_status(self) -> PluginStatus:
        return self._plugin_status
