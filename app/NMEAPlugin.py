import csv
import math
import socket
import threading
from io import StringIO

from events import Events
from geopy.geocoders import Nominatim
from latloncalc.latlon import LatLon, Latitude, Longitude

import config
from app import Helper
from app.Plugin import Plugin


class NMEAPluginEvents(Events):
    __events__ = ('on_connect', 'on_disconnect',)


class NMEAEntry:

    def __init__(self, heading, true_wind_speed, true_wind_direction,
                 apparent_wind_speed, apparent_wind_angle, gps_longitude, gps_latitude,
                 water_temperature, depth, speed_over_ground, speed_over_water,
                 distance_from_previous_entry, cumulative_distance):
        self.heading = heading
        self.true_wind_speed = true_wind_speed
        self.true_wind_direction = true_wind_direction
        self.apparent_wind_speed = apparent_wind_speed
        self.apparent_wind_angle = apparent_wind_angle
        self.gps_longitude = gps_longitude
        self.gps_latitude = gps_latitude
        self.water_temperature = water_temperature
        self.depth = depth
        self.speed_over_ground = speed_over_ground
        self.speed_over_water = speed_over_water
        self.distance_from_previous_entry = distance_from_previous_entry
        self.cumulative_distance = cumulative_distance

    def __str__(self):
        return Helper.get_comma_separated_string(self.get_values())

    def get_values(self):
        lon = self.gps_longitude.to_string("d%°%m%\'%S%\" %H")
        lat = self.gps_latitude.to_string("d%°%m%\'%S%\" %H")
        return [f'{self.heading}', f'{self.true_wind_speed}',
                f'{self.true_wind_direction}', f'{self.apparent_wind_speed}', f'{self.apparent_wind_angle}', lon, lat,
                f'{self.water_temperature}', f'{self.depth}', f'{self.speed_over_ground}',
                f'{self.speed_over_water}', f'{self.distance_from_previous_entry}', f'{self.cumulative_distance}']

    def get_heading(self):
        return self.heading

    def get_true_wind_speed(self):
        return self.true_wind_speed

    def get_true_wind_direction(self):
        return self.true_wind_direction

    def get_apparent_wind_speed(self):
        return self.apparent_wind_speed

    def get_apparent_wind_angle(self):
        return self.apparent_wind_angle

    def get_gps_longitude(self):
        return self.gps_longitude

    def get_gps_latitude(self):
        return self.gps_latitude

    def get_water_temperature(self):
        return self.water_temperature

    def get_depth(self):
        return self.depth

    def get_speed_over_ground(self):
        return self.speed_over_ground

    def get_speed_over_water(self):
        return self.speed_over_water

    def get_distance_from_previous_entry(self):
        return self.distance_from_previous_entry

    def get_cumulative_distance(self):
        return self.cumulative_distance


class NMEAPlugin(Plugin):
    log_entries = []
    server_ip = ''
    server_port = 0

    water_temperature = 0.0
    depth = 0.0
    heading = 0
    gps_latitude = Latitude()
    gps_longitude = Longitude()
    true_wind_speed = 0
    true_wind_direction = 0
    apparent_wind_speed = 0.0
    apparent_wind_angle = 0
    speed_over_water = 0.0
    speed_over_ground = 0.0

    exit_signal = threading.Event()
    nmea_server_thread = None
    events = None

    def __init__(self, args):
        # invoking the __init__ of the parent class
        Plugin.__init__(self, args)

        self.server_ip = args.nmea_server_ip
        self.server_port = int(args.nmea_port)

        self.nmea_server_thread = threading.Thread(target=self.main_thread)
        self.nmea_server_thread.start()

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
        entries_count = len(self.log_entries)
        if self.gps_latitude and self.gps_longitude and entries_count > 0:
            latlon_start = LatLon(self.log_entries[entries_count - 1].get_gps_latitude(),
                                  self.log_entries[entries_count - 1].get_gps_longitude())
            latlon_end = LatLon(self.gps_latitude, self.gps_longitude)
            distance_from_previous_entry = round(float(latlon_end.distance(latlon_start) / 1.852), 1)
            cumulative_distance = round(float(self.log_entries[entries_count - 1].get_cumulative_distance())
                                        + distance_from_previous_entry, 1)

        # Create a new entry
        entry = NMEAEntry(self.heading, self.true_wind_speed, self.true_wind_direction,
                          self.apparent_wind_speed, self.apparent_wind_angle, self.gps_longitude, self.gps_latitude,
                          self.water_temperature, self.depth, self.speed_over_ground, self.speed_over_water,
                          distance_from_previous_entry, cumulative_distance)

        # Add it to the list of entries in memory
        self.log_entries.append(entry)

    def get_metadata_values(self):
        # Return last entry values
        return self.log_entries[len(self.log_entries) - 1].get_values()

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

        if len(self.log_entries) > 0:
            first_entry = self.log_entries[0]
            last_entry = self.log_entries[len(self.log_entries) - 1]

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
            count = len(self.log_entries)
            for entry in self.log_entries:
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
        self.log_entries = []

    def main_thread(self):
        while not self.exit_signal.is_set():
            Helper.console_out(f'Trying to connect to server with address {self.server_ip} on ' +
                               f'port {self.server_port}...')
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(config.DEFAULT_SOCKET_TIMEOUT)

            try:
                client.connect((self.server_ip, self.server_port))

                Helper.console_out(f'Connection to NMEA0183 server established')

                if self.events:
                    self.events.on_connect()

                while True:
                    data = client.recv(config.DEFAULT_BUFFER_SIZE)
                    if data is None:
                        Helper.console_out('No NMEA0183 data received')
                        break

                    str_data = data.decode().rstrip('\r\n')
                    self.process_data(str_data)

            except TimeoutError:
                Helper.console_out(f'Connection to server {self.server_ip} is lost!')
            except OSError:
                Helper.console_out(f'Server {self.server_ip} is down!')
            finally:
                client.close()
                if self.events:
                    self.events.on_disconnect()

    def process_data(self, payload):
        if payload is None:
            return

        buff = StringIO(payload)
        csv_reader = csv.reader(buff)
        csv_list = list(csv_reader)[0]
        str_csv_list_type = csv_list[0]

        # Determine the type of data
        if str_csv_list_type == "$IIHDG":
            if csv_list[1] != '':
                self.heading = math.floor(float(csv_list[1]))
                Helper.console_out(f'Detected heading {self.heading} degrees (True north)')
        elif str_csv_list_type == "$GPGPU":
            if csv_list[2] != '' and csv_list[3] != '' and csv_list[4] != '' and csv_list[5] != '':
                self.gps_latitude = Helper.get_latitude(csv_list[2], csv_list[3])
                self.gps_longitude = Helper.get_longitude(csv_list[4], csv_list[5])
                Helper.console_out(
                    f'Detected GPS coordinates Latitude: {self.gps_latitude} Longitude: {self.gps_longitude}')
        elif str_csv_list_type == "$SDMTW":
            if csv_list[1] != '':
                self.water_temperature = float(csv_list[1])
                Helper.console_out(f'Detected Temperature {self.water_temperature} Celsius')
        elif str_csv_list_type == "$SDDPT":
            if csv_list[1] != '':
                if csv_list[2] != '':
                    self.depth = float(csv_list[1]) + float(csv_list[2])
                else:
                    self.depth = float(csv_list[1])
                self.depth = int(self.depth * 10) / 10
                Helper.console_out(f'Detected depth {self.depth} meters')
        elif str_csv_list_type == "$GPVTG":
            if csv_list[5] != '':
                self.speed_over_ground = csv_list[5]
                Helper.console_out(f'Detected speed over ground {self.speed_over_ground} knots')
        elif str_csv_list_type == "$WIMWD":
            if csv_list[1] != '' and csv_list[5] != '':
                self.true_wind_direction = math.floor(float(csv_list[1]))
                self.true_wind_speed = csv_list[5]
                Helper.console_out(
                    f'Detected true wind direction {self.true_wind_direction} degrees (True north) ' +
                    f'and speed {self.true_wind_speed} knots')
        elif str_csv_list_type == "$WIMWV":
            if csv_list[1] != '' and csv_list[3] != '':
                if self.true_wind_direction != "":
                    self.apparent_wind_angle = math.floor(float(csv_list[1]))
                self.apparent_wind_speed = csv_list[3]
                Helper.console_out(
                    f'Detected apparent wind angle {self.apparent_wind_angle} degrees and ' +
                    f'speed {self.apparent_wind_speed} knots')
        elif str_csv_list_type == "$SDVHW":
            if csv_list[5] != '':
                self.speed_over_water = csv_list[5]
                Helper.console_out(f'Detected speed over water {self.speed_over_water} knots')

    def get_last_latitude_entry(self):
        if len(self.log_entries) > 0:
            return self.log_entries[len(self.log_entries) - 1].get_gps_latitude()
        else:
            return self.gps_latitude

    def get_last_longitude_entry(self):
        if len(self.log_entries) > 0:
            return self.log_entries[len(self.log_entries) - 1].get_gps_longitude()
        else:
            return self.gps_longitude

    def finalize(self):
        self.exit_signal.set()
        self.nmea_server_thread.join()
        Helper.console_out("NMEA plugin worker terminated")

    def raise_events(self, events):
        self.events = events
