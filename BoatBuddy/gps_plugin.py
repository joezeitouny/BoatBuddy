import csv
import math
import threading
from io import BufferedReader
from io import StringIO

from events import Events
from geopy.geocoders import Nominatim
from latloncalc.latlon import LatLon, Latitude, Longitude
from serial import Serial

from BoatBuddy import config, utils
from BoatBuddy.generic_plugin import GenericPlugin, PluginStatus


class GPSPluginEvents(Events):
    __events__ = ('on_connect', 'on_disconnect',)


class GPSEntry:
    def __init__(self, gps_latitude, gps_longitude, location):
        self._gps_latitude = gps_latitude
        self._gps_longitude = gps_longitude
        self._location = location

    def __str__(self):
        return utils.get_comma_separated_string(self.get_values())

    def get_values(self):
        lat = ''
        lon = ''
        if self._gps_latitude != '':
            lat = self._gps_latitude.to_string("d%°%m%\'%S%\" %H")
        if self._gps_longitude != '':
            lon = self._gps_longitude.to_string("d%°%m%\'%S%\" %H")
        return [lat, lon, self._location]

    def get_gps_longitude(self):
        if self._gps_longitude != '':
            return self._gps_longitude
        else:
            return Longitude()

    def get_gps_latitude(self):
        if self._gps_latitude != '':
            return self._gps_latitude
        else:
            return Latitude()

    def get_location(self):
        return self._location


class GPSPlugin(GenericPlugin):
    _events = None
    _stream = None

    def __init__(self, options):
        # invoking the __init__ of the parent class
        GenericPlugin.__init__(self, options)

        # Instance metrics
        self._gps_latitude = ''
        self._gps_longitude = ''
        self._location = ''
        self._gps_fix_captured = False

        # Other instance variables
        self._plugin_status = PluginStatus.STARTING
        self._exit_signal = threading.Event()
        self._timer = threading.Timer(1, self.main_loop)
        self._timer.start()

    def reset_instance_metrics(self):
        self._gps_latitude = ''
        self._gps_longitude = ''
        self._location = ''
        self._gps_fix_captured = False

    def get_metadata_headers(self):
        return config.GPS_PLUGIN_METADATA_HEADERS.copy()

    def take_snapshot(self, store_entry):
        # Create a new entry
        entry = GPSEntry(self._gps_latitude, self._gps_longitude, self._location)

        # Add it to the list of entries in memory
        if store_entry:
            self._log_entries.append(entry)

        return entry

    def get_metadata_values(self):
        # Return last entry values
        return self._log_entries[len(self._log_entries) - 1].get_values()

    def get_summary_headers(self):
        return config.GPS_PLUGIN_SUMMARY_HEADERS.copy()

    def get_summary_values(self):
        log_summary_list = []

        if len(self._log_entries) > 0:
            # Collect the GPS coordinates from the first entry which has valid ones
            first_gps_latitude_entry = Latitude()
            first_gps_longitude_entry = Longitude()
            n = 0
            while n < len(self._log_entries):
                entry = self._log_entries[n]
                if entry.get_gps_latitude().to_string("D") != Latitude().to_string("D") and \
                        entry.get_gps_longitude().to_string("D") != Longitude().to_string("D") and \
                        LatLon(entry.get_gps_latitude(), entry.get_gps_longitude()).to_string("D") \
                        != LatLon(Latitude(), Longitude()).to_string("D"):
                    first_gps_latitude_entry = entry.get_gps_latitude()
                    first_gps_longitude_entry = entry.get_gps_longitude()
                    break
                n = n + 1

            # Collect the GPS coordinates from the last entry which has valid ones
            last_gps_latitude_entry = Latitude()
            last_gps_longitude_entry = Longitude()
            n = len(self._log_entries)
            while n > 0:
                entry = self._log_entries[n - 1]
                if entry.get_gps_latitude().to_string("D") != Latitude().to_string("D") and \
                        entry.get_gps_longitude().to_string("D") != Longitude().to_string("D") and \
                        LatLon(entry.get_gps_latitude(), entry.get_gps_longitude()).to_string("D") \
                        != LatLon(Latitude(), Longitude()).to_string("D"):
                    last_gps_latitude_entry = entry.get_gps_latitude()
                    last_gps_longitude_entry = entry.get_gps_longitude()
                    break
                n = n - 1

            # Try to fetch the starting and ending location cities
            geolocator = Nominatim(user_agent="BoatBuddy")
            starting_location_str = ''
            try:
                starting_location = geolocator.reverse(f'{first_gps_latitude_entry}' + ',' +
                                                       f'{first_gps_longitude_entry}')
                starting_location_str = starting_location.raw['address'].get('city', '') + ', ' + starting_location.raw[
                    'address'].get('country', '')
            except Exception as e:
                utils.get_logger().debug(f'Could not get location from GPS coordinates. Details: {e}')
            log_summary_list.append(starting_location_str)

            ending_location_str = ''
            try:
                ending_location = geolocator.reverse(f'{last_gps_latitude_entry}' + ',' +
                                                     f'{last_gps_longitude_entry}')
                ending_location_str = ending_location.raw['address'].get('city', '') + ', ' + ending_location.raw[
                    'address'].get('country', '')
            except Exception as e:
                utils.get_logger().debug(f'Could not get location from GPS coordinates. Details: {e}')
            log_summary_list.append(ending_location_str)

            log_summary_list.append(first_gps_latitude_entry.to_string("d%°%m%\'%S%\" %H"))
            log_summary_list.append(first_gps_longitude_entry.to_string("d%°%m%\'%S%\" %H"))
            log_summary_list.append(last_gps_latitude_entry.to_string("d%°%m%\'%S%\" %H"))
            log_summary_list.append(last_gps_longitude_entry.to_string("d%°%m%\'%S%\" %H"))

            # Calculate travelled distance and heading
            latlon_start = LatLon(first_gps_latitude_entry, first_gps_longitude_entry)
            latlon_end = LatLon(last_gps_latitude_entry, last_gps_longitude_entry)
            if latlon_start.to_string("D") != latlon_end.to_string("D"):
                distance = round(float(latlon_end.distance(latlon_start) / 1.852), 2)
                log_summary_list.append(distance)
                heading = math.floor(float(latlon_end.heading_initial(latlon_start)))
                log_summary_list.append(heading)
            else:
                log_summary_list.append(0)
                log_summary_list.append('')
        else:
            log_summary_list = ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

        return log_summary_list

    def main_loop(self):
        if self._exit_signal.is_set():
            self._plugin_status = PluginStatus.DOWN
            utils.get_logger().info('GPS plugin instance is ready to be destroyed')
            return

        try:
            # Get gps position
            with Serial(self._options.gps_serial_port, 4800, bytesize=8, stopbits=1.0, parity='N',
                        xonxoff=0, rtscts=0, timeout=0.1) as self._serial_object:
                self._stream = BufferedReader(self._serial_object)

                while not self._exit_signal.is_set():
                    try:
                        raw_data = self._stream.readline()
                        if raw_data is not None:
                            if self._plugin_status != PluginStatus.RUNNING:
                                utils.get_logger().info(f'Connection to GPS module is established')
                                self._plugin_status = PluginStatus.RUNNING

                                self.reset_instance_metrics()

                                if self._events:
                                    self._events.on_connect()

                            str_data = raw_data.decode().rstrip('\r\n')
                            utils.get_logger().debug(str_data)
                            self._process_data(str_data)
                    except Exception as e:
                        utils.get_logger().debug(f"Error parsing data stream {e}")
                        continue
        except Exception as e:
            self._handle_connection_exception(e)

    def _process_data(self, payload):
        if payload is None:
            return

        buff = StringIO(payload)
        csv_reader = csv.reader(buff)
        csv_list = list(csv_reader)[0]

        if not csv_list[0]:
            return

        # Determine the type of data
        if not str(csv_list[0]).endswith('GLL'):
            return

        if csv_list[6] and csv_list[6] == 'A':
            self._gps_latitude = utils.get_latitude(csv_list[1], csv_list[2])
            self._gps_longitude = utils.get_longitude(csv_list[3], csv_list[4])
            self._gps_fix_captured = True
            utils.get_logger().debug(
                f'Detected GPS coordinates Latitude: {self._gps_latitude} Longitude: {self._gps_longitude}')

            geolocator = Nominatim(user_agent="BoatBuddy")
            try:
                geo_location = geolocator.reverse(f'{self._gps_latitude}' + ',' +
                                                  f'{self._gps_longitude}')
                self._location = geo_location.raw['address'].get('city', '') + ', ' + geo_location.raw[
                    'address'].get(
                    'country', '')
            except Exception as e:
                utils.get_logger().debug(f'Could not get location from GPS coordinates. Details: {e}')

    def _handle_connection_exception(self, message):
        if self._plugin_status != PluginStatus.DOWN:
            utils.get_logger().info(f'GPS system is unreachable. Details: {message}')

            self._plugin_status = PluginStatus.DOWN

            # If anyone is listening to events then notify of a disconnection
            if self._events:
                self._events.on_disconnect()

        # Reset the timer
        self._timer = self._timer = threading.Timer(config.GPS_TIMER_INTERVAL, self.main_loop)
        self._timer.start()

    def finalize(self):
        self._exit_signal.set()
        if self._timer:
            self._timer.cancel()
        utils.get_logger().info("GPS plugin worker thread notified...")

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
