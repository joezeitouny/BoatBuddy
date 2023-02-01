import csv
import math
import optparse
import socket
import threading
import time
from datetime import datetime
from io import StringIO
from time import mktime

import gpxpy
import gpxpy.gpx
import openpyxl
from geopy.geocoders import Nominatim
from latloncalc.latlon import LatLon, Latitude, Longitude

from VictronPlugin import VictronPlugin

DEFAULT_TCP_PORT = 10110
DEFAULT_BUFFER_SIZE = 4096
DEFAULT_SOCKET_TIMEOUT = 60
DEFAULT_DISK_WRITE_INTERVAL = 5
DEFAULT_FILENAME_PREFIX = "Trip_"
DEFAULT_EXCEL_OUTPUT_FLAG = False
DEFAULT_CSV_OUTPUT_FLAG = False
DEFAULT_GPX_OUTPUT_FLAG = False
DEFAULT_SUMMARY_OUTPUT_FLAG = False
DEFAULT_SUMMARY_FILENAME_PREFIX = "Trip_Summary_"
DEFAULT_VERBOSE_FLAG = False

verbose_flag = DEFAULT_VERBOSE_FLAG


def print_string(string_to_print):
    if verbose_flag:
        print(string_to_print)


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


@staticmethod
def get_degrees(coord_str):
    if len(coord_str.split('.')[0]) == 5:
        # We're dealing with negative coordinates here
        return float(coord_str[1:3])
    else:
        return float(coord_str[:2])


@staticmethod
def get_minutes(coord_str):
    return float(coord_str.split('.')[0][-2:])


@staticmethod
def get_seconds(coord_str):
    return (0.1 * float(coord_str.split('.')[1]) * 60) / 1000


@staticmethod
def get_latitude(coord_str, hemispehere):
    lat = Latitude(get_degrees(coord_str), get_minutes(coord_str),
                   get_seconds(coord_str))
    lat.set_hemisphere(hemispehere)
    return lat


@staticmethod
def get_longitude(coord_str, hemispehere):
    lon = Longitude(get_degrees(coord_str), get_minutes(coord_str),
                    get_seconds(coord_str))
    lon.set_hemisphere(hemispehere)
    return lon


class LogEntry:

    def __init__(self, utc_time, local_time, heading, true_wind_speed, true_wind_direction,
                 apparent_wind_speed, apparent_wind_angle, gps_longitude, gps_latitude,
                 water_temperature, depth, speed_over_ground, speed_over_water,
                 distance_from_previous_entry, cumulative_distance):
        self.utc_time = utc_time
        self.local_time = local_time
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
        return get_comma_separated_string(self.get_values())

    @staticmethod
    def get_headers():
        return ["UTC Timestamp", "Local Timestamp", "True Heading (degrees)", "True Wind Speed (knots)",
                "True Wind Direction (degrees)", "Apparent Wind Speed (knots)",
                "Apparent Wind Angle (Relative degrees)", "GPS Longitude (d°m\'S\" H)",
                "GPS Latitude (d°m\'S\" H)", "Water Temperature (°C)",
                "Depth (meters)", "Speed Over Ground (knots)", "Speed Over Water (knots)",
                "Distance From Previous Entry (miles)", "Cumulative Distance (miles)"]

    def get_values(self):
        lon = self.gps_longitude.to_string("d%°%m%\'%S%\" %H")
        lat = self.gps_latitude.to_string("d%°%m%\'%S%\" %H")
        return [f'{time.strftime("%Y-%m-%d %H:%M:%S", self.utc_time)}',
                f'{time.strftime("%Y-%m-%d %H:%M:%S", self.local_time)}',
                f'{self.heading}', f'{self.true_wind_speed}',
                f'{self.true_wind_direction}', f'{self.apparent_wind_speed}', f'{self.apparent_wind_angle}', lon, lat,
                f'{self.water_temperature}', f'{self.depth}', f'{self.speed_over_ground}',
                f'{self.speed_over_water}', f'{self.distance_from_previous_entry}', f'{self.cumulative_distance}']

    def get_utc_timestamp(self):
        return self.utc_time

    def get_local_timestamp(self):
        return self.local_time

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


class Log:
    log_entries = []

    def __init__(self, utc_time, local_time, filename_prefix):
        self.utc_time = utc_time
        self.local_time = local_time
        suffix = time.strftime("%Y%m%d%H%M%S", utc_time)
        self.name = f'{filename_prefix}{suffix}'

    def get_utc_time(self):
        return self.utc_time

    def get_name(self):
        return self.name

    def add_entry(self, entry):
        if entry is not None:
            self.log_entries.append(entry)

    def get_entries(self):
        return self.log_entries


class LogManager:
    disk_write_interval = 0
    excel_output = False
    csv_output = False
    gpx_output = False
    summary_output = False
    summary_filename_prefix = ""

    log = None
    victron_plugin = None
    workbook = None
    sheet = None

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
    disk_write_thread_is_running = False
    gpx = None
    gpx_track = None
    gpx_segment = None

    def __init__(self, filename_prefix, disk_write_interval, excel_output, csv_output, gpx_output, summary_output,
                 summary_filename_prefix, victron_server_ip):
        self.log = Log(time.gmtime(), time.localtime(), filename_prefix)
        self.disk_write_interval = disk_write_interval
        self.excel_output = excel_output
        self.csv_output = csv_output
        self.gpx_output = gpx_output
        self.summary_output = summary_output
        self.summary_filename_prefix = summary_filename_prefix
        column_headers = LogEntry.get_headers()

        if victron_server_ip:
            self.victron_plugin = VictronPlugin([victron_server_ip])
            column_headers += self.victron_plugin.get_metadata_headers()

        if self.csv_output:
            # Add the columns headers to the beginning of the csv file
            with open(f"{self.log.get_name()}.csv", "a") as file:
                file.write(f'{get_comma_separated_string(column_headers)}\r\n')

        if self.excel_output:
            # Create an Excel workbook
            self.workbook = openpyxl.Workbook()

            # Create a sheet in the workbook
            self.sheet = self.workbook.active

            # Create the header row
            self.sheet.append(column_headers)

        if self.gpx_output:
            # Creating a new GPX object
            self.gpx = gpxpy.gpx.GPX()

            # Create first track in our GPX:
            self.gpx_track = gpxpy.gpx.GPXTrack()
            self.gpx.tracks.append(self.gpx_track)

            # Create first segment in our GPX track:
            self.gpx_segment = gpxpy.gpx.GPXTrackSegment()
            self.gpx_track.segments.append(self.gpx_segment)

        print_string(f'New log session initialized {self.log.get_name()}')

        threading.Timer(self.disk_write_interval, self.start_disk_helper_thread).start()

    def start_disk_helper_thread(self):
        self.disk_write_thread_is_running = True
        threading.Thread(target=self.write_log_data_to_disk()).start()

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
                print_string(f'Detected heading {self.heading} degrees (True north)')
        elif str_csv_list_type == "$GPGGA":
            if csv_list[2] != '' and csv_list[3] != '' and csv_list[4] != '' and csv_list[5] != '':
                self.gps_latitude = get_latitude(csv_list[2], csv_list[3])
                self.gps_longitude = get_longitude(csv_list[4], csv_list[5])
                print_string(
                    f'Detected GPS coordinates Latitude: {self.gps_latitude} Longitude: {self.gps_longitude}')
        elif str_csv_list_type == "$SDMTW":
            if csv_list[1] != '':
                self.water_temperature = float(csv_list[1])
                print_string(f'Detected Temperature {self.water_temperature} Celsius')
        elif str_csv_list_type == "$SDDPT":
            if csv_list[1] != '':
                if csv_list[2] != '':
                    self.depth = float(csv_list[1]) + float(csv_list[2])
                else:
                    self.depth = float(csv_list[1])
                self.depth = int(self.depth * 10) / 10
                print_string(f'Detected depth {self.depth} meters')
        elif str_csv_list_type == "$GPVTG":
            if csv_list[5] != '':
                self.speed_over_ground = csv_list[5]
                print_string(f'Detected speed over ground {self.speed_over_ground} knots')
        elif str_csv_list_type == "$WIMWD":
            if csv_list[1] != '' and csv_list[5] != '':
                self.true_wind_direction = math.floor(float(csv_list[1]))
                self.true_wind_speed = csv_list[5]
                print_string(
                    f'Detected true wind direction {self.true_wind_direction} degrees (True north) ' +
                    f'and speed {self.true_wind_speed} knots')
        elif str_csv_list_type == "$WIMWV":
            if csv_list[1] != '' and csv_list[3] != '':
                if self.true_wind_direction != "":
                    self.apparent_wind_angle = math.floor(float(csv_list[1]))
                self.apparent_wind_speed = csv_list[3]
                print_string(
                    f'Detected apparent wind angle {self.apparent_wind_angle} degrees and ' +
                    f'speed {self.apparent_wind_speed} knots')
        elif str_csv_list_type == "$SDVHW":
            if csv_list[5] != '':
                self.speed_over_water = csv_list[5]
                print_string(f'Detected speed over water {self.speed_over_water} knots')

    def write_log_data_to_disk(self):
        while self.disk_write_thread_is_running:
            # Calculate the distance traveled so far and the distance from the last recorded entry
            cumulative_distance = 0.0
            distance_from_previous_entry = 0.0
            entries_count = len(self.log.get_entries())
            if self.gps_latitude and self.gps_longitude and entries_count > 0:
                latlon_start = LatLon(self.log.get_entries()[entries_count - 1].get_gps_latitude(),
                                      self.log.get_entries()[entries_count - 1].get_gps_longitude())
                latlon_end = LatLon(self.gps_latitude, self.gps_longitude)
                distance_from_previous_entry = round(float(latlon_end.distance(latlon_start) / 1.852), 1)
                cumulative_distance = round(float(self.log.get_entries()[entries_count - 1].get_cumulative_distance())
                                            + distance_from_previous_entry, 1)

            # Create a log entry and add it to the log entries list
            log_entry = LogEntry(time.gmtime(), time.localtime(), self.heading, self.true_wind_speed,
                                 self.true_wind_direction,
                                 self.apparent_wind_speed, self.apparent_wind_angle, self.gps_longitude,
                                 self.gps_latitude, self.water_temperature, self.depth,
                                 self.speed_over_ground, self.speed_over_water, distance_from_previous_entry,
                                 cumulative_distance)

            # Add this entry to the log object entries collection store
            self.log.add_entry(log_entry)

            # Write log contents to disk
            print_string("Writing collected data to disk")

            column_values = log_entry.get_values()

            if self.victron_plugin:
                column_values += self.victron_plugin.get_metadata_values(print_func=print_string)

            # Append the last added entry to the file on disk
            if self.csv_output:
                with open(f"{self.log.get_name()}.csv", "a") as file:
                    file.write(f'{get_comma_separated_string(column_values)}\r\n')

            if self.excel_output:
                # Add the name and price to the sheet
                self.sheet.append(column_values)

                # Save the workbook
                self.workbook.save(filename=f"{self.log.get_name()}.xlsx")

            if self.gpx_output:
                # Append new GPX track point
                self.gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(latitude=log_entry.get_gps_latitude(),
                                                                       longitude=log_entry.get_gps_longitude(),
                                                                       time=datetime.fromtimestamp(
                                                                           mktime(log_entry.get_utc_timestamp()))))

                # Write the new contents of the GPX file to disk
                with open(f"{self.log.get_name()}.gpx", 'w') as file:
                    file.write(f'{self.gpx.to_xml()}')

            # Sleep for the specified interval
            time.sleep(self.disk_write_interval)

    def end_session(self):
        print_string("Ending session")

        # Stop the running thread that captures log entries
        self.disk_write_thread_is_running = False

        # if the summary option is set then build a log summary excel workbook
        if self.summary_output:
            # Create an Excel workbook
            summary_workbook = openpyxl.Workbook()

            # Create a sheet in the workbook
            summary_sheet = summary_workbook.active

            # Create the header row
            summary_sheet.append(["Starting Timestamp (UTC)", "Starting Timestamp (Local)", "Ending Timestamp (UTC)",
                                  "Ending Timestamp (Local)", "Starting Location (City, Country)",
                                  "Ending Location (City, Country)", "Starting GPS Latitude (d°m\'S\" H)",
                                  "Starting GPS Longitude (d°m\'S\" H)", "Ending GPS Latitude (d°m\'S\" H)",
                                  "Ending GPS Longitude (d°m\'S\" H)", "Distance (miles)", "Heading (degrees)",
                                  "Average Wind Speed (knots)", "Average Wind Direction (degrees)",
                                  "Average Water Temperature (°C)", "Average Depth (meters)",
                                  "Average Speed Over Ground (knots)", "Average Speed Over Water (knots)"])

            log_summary_list = []

            if len(self.log.get_entries()) > 0:
                first_entry = self.log.get_entries()[0]
                last_entry = self.log.get_entries()[len(self.log.get_entries()) - 1]

                # Collect timestamps
                log_summary_list.append(f'{time.strftime("%Y-%m-%d %H:%M:%S", first_entry.get_utc_timestamp())}')
                log_summary_list.append(f'{time.strftime("%Y-%m-%d %H:%M:%S", first_entry.get_local_timestamp())}')
                log_summary_list.append(f'{time.strftime("%Y-%m-%d %H:%M:%S", last_entry.get_utc_timestamp())}')
                log_summary_list.append(f'{time.strftime("%Y-%m-%d %H:%M:%S", last_entry.get_local_timestamp())}')

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
                count = len(self.log.get_entries())
                for entry in self.log.get_entries():
                    sum_wind_speed += float(entry.get_true_wind_speed())
                    sum_true_wind_direction += int(entry.get_true_wind_direction())
                    sum_water_temperature += float(entry.get_water_temperature())
                    sum_depth += float(entry.get_depth())
                    sum_speed_over_ground += float(entry.get_speed_over_ground())
                    sum_speed_over_water += float(entry.get_speed_over_water())

                log_summary_list.append(sum_wind_speed / count)
                log_summary_list.append(int(sum_true_wind_direction / count))
                log_summary_list.append(sum_water_temperature / count)
                log_summary_list.append(sum_depth / count)
                log_summary_list.append(sum_speed_over_ground / count)
                log_summary_list.append(sum_speed_over_water / count)

                # Add the name and price to the sheet
                summary_sheet.append(log_summary_list)

            # Save the workbook
            workbook_filename = self.summary_filename_prefix + time.strftime("%Y%m%d%H%M%S", self.log.get_utc_time())
            summary_workbook.save(filename=f"{workbook_filename}.xlsx")


def start_logging(server_ip, server_port, disk_write_interval, filename_prefix, excel, csv, gpx, summary,
                  summary_filename, victron_server_ip):
    log_manager = None

    while True:
        print_string(f'Trying to connect to server with address {server_ip} on port {server_port}...')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(60)

        try:
            client.connect((server_ip, server_port))

            print_string("Connection established")

            log_manager = LogManager(filename_prefix, disk_write_interval, excel, csv, gpx, summary, summary_filename,
                                     victron_server_ip)

            while True:
                data = client.recv(DEFAULT_BUFFER_SIZE)
                if data is None:
                    print_string('No data received')
                    break

                str_data = data.decode().rstrip('\r\n')

                # print(f'Data received: {str_data}')
                LogManager.process_data(log_manager, str_data)

        except TimeoutError:
            print_string("Connection timeout")
        finally:
            print_string("Closing connections if any")
            client.close()
            if log_manager is not None:
                log_manager.end_session()


if __name__ == '__main__':
    # Create an options list using the Options Parser
    parser = optparse.OptionParser()
    parser.set_usage("%prog host [options]")
    parser.set_defaults(port=DEFAULT_TCP_PORT, filename=DEFAULT_FILENAME_PREFIX, interval=DEFAULT_DISK_WRITE_INTERVAL,
                        excel=DEFAULT_EXCEL_OUTPUT_FLAG, csv=DEFAULT_CSV_OUTPUT_FLAG, gpx=DEFAULT_GPX_OUTPUT_FLAG,
                        summary=DEFAULT_SUMMARY_OUTPUT_FLAG, summary_filename=DEFAULT_SUMMARY_FILENAME_PREFIX,
                        verbose=DEFAULT_VERBOSE_FLAG)
    parser.add_option('--port', dest='port', type='int', help=f'NMEA0183 host port. Default is: {DEFAULT_TCP_PORT}')
    parser.add_option('-i', '--interval', type='float', dest='interval',
                      help=f'Disk write interval (in seconds). Default is: {DEFAULT_DISK_WRITE_INTERVAL} seconds')
    parser.add_option('--excel', action='store_true', dest='excel', help='Generate an Excel workbook.')
    parser.add_option('--csv', action='store_true', dest='csv', help='Generate a comma separated list (CSV) file.')
    parser.add_option('--gpx', action='store_true', dest='gpx', help=f'Generate a GPX file.')
    parser.add_option('-f', '--file', dest='filename', type='string', help='Output filename prefix. ' +
                                                                           f'Default is: {DEFAULT_FILENAME_PREFIX}')
    parser.add_option('--summary', action='store_true', dest='summary',
                      help=f'Generate a trip summary excel workbook at the end of the session.')
    parser.add_option('--summary-filename-prefix', dest='summary_filename', type='string',
                      help=f'Summary filename prefix. Default is: {DEFAULT_SUMMARY_FILENAME_PREFIX}')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                      help=f'Verbose mode. Print debugging messages about captured data. ' +
                           f'This is helpful in debugging connection, and configuration problems.')
    parser.add_option('--victron-server-ip', dest='victron_server_ip', type='string',
                      help=f'Append Victron system metrics from the specified device IP')
    (options, args) = parser.parse_args()

    # If the host address is not provided
    if len(args) == 0:
        print(f'Error: Host Address is required\r\n')
        parser.print_help()
    elif not options.excel and not options.gpx and not options.csv and not options.summary:
        print(f'Error: At least one output medium needs to be specified\r\n')
        parser.print_help()
    else:
        verbose_flag = options.verbose
        start_logging(args[0], options.port, options.interval, options.filename, options.excel,
                      options.csv, options.gpx, options.summary, options.summary_filename, options.victron_server_ip)
