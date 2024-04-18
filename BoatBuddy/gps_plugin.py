import csv
import math
import threading
import time
from io import BufferedReader
from io import StringIO

from events import Events
from geopy.geocoders import Nominatim
from latloncalc.latlon import LatLon, Latitude, Longitude, string2latlon
from serial import Serial

from BoatBuddy import globals, utils
from BoatBuddy.generic_plugin import GenericPlugin, PluginStatus


class GPSPluginEvents(Events):
    __events__ = ('on_connect', 'on_disconnect',)


class GPSEntry:
    def __init__(self, gps_latitude, gps_longitude, location, speed_over_ground, course_over_ground,
                 distance_from_previous_entry, cumulative_distance):
        self._gps_latitude = gps_latitude
        self._gps_longitude = gps_longitude
        self._location = location
        self._speed_over_ground = speed_over_ground
        self._course_over_ground = course_over_ground
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
        return [lat, lon, self._location, self._speed_over_ground, self._course_over_ground,
                self._distance_from_previous_entry, self._cumulative_distance]

    def get_gps_longitude(self):
        return self._gps_longitude

    def get_gps_latitude(self):
        return self._gps_latitude

    def get_location(self):
        return self._location

    def get_speed_over_ground(self):
        return self._speed_over_ground

    def get_course_over_ground(self):
        return self._course_over_ground

    def get_distance_from_previous_entry(self):
        return self._distance_from_previous_entry

    def get_cumulative_distance(self):
        return self._cumulative_distance


class GPSPlugin(GenericPlugin):
    _events = None
    _stream = None

    def __init__(self, options, log_manager):
        # invoking the __init__ of the parent class
        GenericPlugin.__init__(self, options, log_manager)

        # Instance metrics
        self._gps_latitude = globals.EMPTY_METRIC_VALUE
        self._gps_longitude = globals.EMPTY_METRIC_VALUE
        self._location = globals.EMPTY_METRIC_VALUE
        self._speed_over_ground = globals.EMPTY_METRIC_VALUE
        self._course_over_ground = globals.EMPTY_METRIC_VALUE
        self._pdop = globals.EMPTY_METRIC_VALUE
        self._gps_fix_captured = False
        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]
        self._sum_sog = 0
        self._cnt_sog_entries = 0

        # Other instance variables
        self._plugin_status = PluginStatus.STARTING
        self._exit_signal = threading.Event()
        self._timer = threading.Timer(1, self.main_loop)
        self._timer.start()
        self._log_manager.info('GPS module successfully started!')

    def reset_instance_metrics(self):
        self._gps_latitude = globals.EMPTY_METRIC_VALUE
        self._gps_longitude = globals.EMPTY_METRIC_VALUE
        self._location = globals.EMPTY_METRIC_VALUE
        self._speed_over_ground = globals.EMPTY_METRIC_VALUE
        self._course_over_ground = globals.EMPTY_METRIC_VALUE
        self._pdop = globals.EMPTY_METRIC_VALUE
        self._gps_fix_captured = False
        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]
        self._sum_sog = 0
        self._cnt_sog_entries = 0

    def get_metadata_headers(self):
        return globals.GPS_PLUGIN_METADATA_HEADERS.copy()

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
        entry = GPSEntry(self._gps_latitude, self._gps_longitude, self._location, self._speed_over_ground,
                         self._course_over_ground, distance_from_previous_entry, cumulative_distance)

        # Add it to the list of entries in memory
        if store_entry:
            self._log_entries.append(entry)

            # calculate summary values
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
            if entry.get_speed_over_ground() != globals.EMPTY_METRIC_VALUE:
                self._sum_sog += utils.try_parse_float(entry.get_speed_over_ground())
                self._cnt_sog_entries += 1
                if self._summary_values[8] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[8] = entry.get_speed_over_ground()
                else:
                    self._summary_values[8] = round(self._sum_sog / self._cnt_sog_entries, 1)

        return entry

    def get_metadata_values(self):
        # Return last entry values
        return self._log_entries[len(self._log_entries) - 1].get_values()

    def get_summary_headers(self):
        return globals.GPS_PLUGIN_SUMMARY_HEADERS.copy()

    def get_summary_values(self, reverse_lookup_locations=False):
        if reverse_lookup_locations:
            geolocator = Nominatim(user_agent="BoatBuddy")
            if self._summary_values[2] != globals.EMPTY_METRIC_VALUE and\
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

            if self._summary_values[4] != globals.EMPTY_METRIC_VALUE and\
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

    def main_loop(self):
        if self._exit_signal.is_set():
            self._plugin_status = PluginStatus.DOWN
            self._log_manager.info('GPS plugin instance is ready to be destroyed')
            return

        try:
            # Get gps position
            with Serial(self._options.gps_serial_port, 4800, bytesize=8, stopbits=1.0, parity='N',
                        xonxoff=0, rtscts=0, timeout=0.1) as self._serial_object:
                self._stream = BufferedReader(self._serial_object)

                while not self._exit_signal.is_set():
                    raw_data = self._stream.readline()

                    if raw_data is None:
                        raise ValueError(f'No data received')

                    str_data = raw_data.decode().rstrip('\r\n')
                    self._log_manager.debug(str_data)
                    self._process_data(str_data)

                    time.sleep(globals.GPS_PLUGIN_SAMPLING_RATE)  # Sleep for one second
        except Exception as e:
            self._handle_connection_exception(e)

    def _process_data(self, payload):
        if payload is None:
            return

        buff = StringIO(payload)
        csv_reader = csv.reader(buff)

        if not csv_reader:
            return

        csv_reader_list = list(csv_reader)

        if len(csv_reader_list) == 0:
            return

        csv_list = csv_reader_list[0]

        if not csv_list[0]:
            return

        # Determine the type of data
        if str(csv_list[0]).endswith('GLL') and csv_list[6] == 'A':
            if self._plugin_status != PluginStatus.RUNNING:
                self._log_manager.info(f'Connection to GPS module is established')
                self._plugin_status = PluginStatus.RUNNING

                self.reset_instance_metrics()

                if self._events:
                    self._events.on_connect()

            self._gps_latitude = utils.get_latitude(csv_list[1], csv_list[2])
            self._gps_longitude = utils.get_longitude(csv_list[3], csv_list[4])
            self._gps_fix_captured = True
            self._log_manager.debug(
                f'Detected GPS coordinates Latitude: {self._gps_latitude} Longitude: {self._gps_longitude}')

            geolocator = Nominatim(user_agent="BoatBuddy")
            try:
                geo_location = geolocator.reverse(f'{self._gps_latitude}' + ',' +
                                                  f'{self._gps_longitude}')
                self._location = geo_location.raw['address'].get('city', '') + ', ' + geo_location.raw[
                    'address'].get(
                    'country', '')
            except Exception as e:
                self._log_manager.debug(f'Could not get location from GPS coordinates. Details: {e}')
        elif str(csv_list[0]).endswith('VTG'):
            self._course_over_ground = utils.try_parse_float(csv_list[1])
            self._speed_over_ground = round(utils.try_parse_float(csv_list[5]), 1)
            self._log_manager.debug(
                f'Detected COG: {self._course_over_ground} SOG: {self._speed_over_ground}')
        elif str(csv_list[0]).endswith('GSA'):
            self._pdop = utils.try_parse_float(csv_list[15])

    def _handle_connection_exception(self, message):
        if self._plugin_status != PluginStatus.DOWN:
            self._log_manager.info(f'GPS system is unreachable. Details: {message}')

            self._plugin_status = PluginStatus.DOWN

            # If anyone is listening to events then notify of a disconnection
            if self._events:
                self._events.on_disconnect()

        # Reset the timer
        self._timer = threading.Timer(globals.GPS_TIMER_INTERVAL, self.main_loop)
        self._timer.start()

    def finalize(self):
        self._exit_signal.set()
        if self._timer:
            self._timer.cancel()
        self._log_manager.info("GPS plugin worker thread notified...")

    def get_status(self) -> PluginStatus:
        return self._plugin_status

    def register_for_events(self, events):
        self._events = events

    def is_gps_fix_captured(self):
        return self._gps_fix_captured

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

    def get_accuracy(self):
        if self._pdop == globals.EMPTY_METRIC_VALUE:
            return

        if self._pdop <= 2:
            return 'Excellent'
        elif 2 < self._pdop <= 5:
            return 'Good'
        elif 5 < self._pdop <= 10:
            return 'Moderate'
        elif 10 < self._pdop <= 20:
            return 'Fair'
        elif 20 < self._pdop <= 50:
            return 'Poor'
        else:
            return 'Very Poor'
