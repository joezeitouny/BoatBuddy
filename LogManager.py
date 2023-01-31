from LogEntry import LogEntry
from io import StringIO
import gpxpy
import gpxpy.gpx
from latloncalc.latlon import Latitude, Longitude
import openpyxl
import time
import csv
import threading


class LogManager:

    log_name = ""
    disk_write_interval = 0
    excel_output = False
    csv_output = False
    gpx_output = False
    workbook = None
    sheet = None

    water_temperature = ""
    depth = ""
    heading = ""
    gps_latitude = None
    gps_longitude = None
    gps_elevation = ""
    speed_over_ground = ""
    true_wind_speed = ""
    true_wind_direction = ""
    apparent_wind_speed = ""
    apparent_wind_angle = ""
    speed_over_water = ""
    disk_write_thread_is_running = False
    gpx = None
    gpx_track = None
    gpx_segment = None

    def __init__(self, filename_prefix, disk_write_interval, excel_output, csv_output, gpx_output):
        suffix = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        self.log_name = f'{filename_prefix}{suffix}'
        self.disk_write_interval = disk_write_interval
        self.excel_output = excel_output
        self.csv_output = csv_output
        self.gpx_output = gpx_output

        if self.excel_output:
            # Create an Excel workbook
            self.workbook = openpyxl.Workbook()

            # Create a sheet in the workbook
            self.sheet = self.workbook.active

            # Create the header row
            self.sheet.append(["UTC Timestamp", "Local Timestamp", "True Heading (degrees)", "True Wind Speed (knots)",
                               "True Wind Direction (degrees)", "Apparent Wind Speed (knots)",
                               "Apparent Wind Angle (Relative degrees)", "GPS Longitude (d°m\'S\" H)",
                               "GPS Latitude (d°m\'S\" H)", "GPS Elevation (meters)", "Water Temperature (°C)",
                               "Depth (meters)", "Speed Over Ground (knots)", "Speed Over Water (knots)"])

        if self.gpx_output:
            # Creating a new file:
            # --------------------
            self.gpx = gpxpy.gpx.GPX()

            # Create first track in our GPX:
            self.gpx_track = gpxpy.gpx.GPXTrack()
            self.gpx.tracks.append(self.gpx_track)

            # Create first segment in our GPX track:
            self.gpx_segment = gpxpy.gpx.GPXTrackSegment()
            self.gpx_track.segments.append(self.gpx_segment)

        print(f'New Log file initialized {self.log_name}')

        threading.Timer(self.disk_write_interval, self.start_disk_helper_thread).start()

    def start_disk_helper_thread(self):
        self.disk_write_thread_is_running = True
        threading.Thread(target=self.write_log_data_to_disk()).start()

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
        lat = Latitude(LogManager.get_degrees(coord_str), LogManager.get_minutes(coord_str),
                       LogManager.get_seconds(coord_str))
        lat.set_hemisphere(hemispehere)
        return lat

    @staticmethod
    def get_longitude(coord_str, hemispehere):
        lon = Longitude(LogManager.get_degrees(coord_str), LogManager.get_minutes(coord_str),
                        LogManager.get_seconds(coord_str))
        lon.set_hemisphere(hemispehere)
        return lon

    def process_data(self, payload):
        if payload is None:
            return

        buff = StringIO(payload)
        csv_reader = csv.reader(buff)
        csv_list = list(csv_reader)[0]
        str_csv_list_type = csv_list[0]

        # Determine the type of data
        if str_csv_list_type == "$IIHDG":
            self.heading = csv_list[1]
            print(f'Detected heading {self.heading} degrees (True north)')
        elif str_csv_list_type == "$GPGGA":
            self.gps_latitude = LogManager.get_latitude(csv_list[2], csv_list[3])
            self.gps_longitude = LogManager.get_longitude(csv_list[4], csv_list[5])
            self.gps_elevation = csv_list[9]
            print(
                f'Detected GPS coordinates Latitude: {self.gps_latitude} Longitude: {self.gps_longitude} '
                + f'Elevation: {self.gps_elevation} meters')
        elif str_csv_list_type == "$SDMTW":
            self.water_temperature = csv_list[1]
            print(f'Detected Temperature {self.water_temperature} Celsius')
        elif str_csv_list_type == "$SDDPT":
            depth = 0
            if csv_list[2] != '':
                depth = float(csv_list[1]) + float(csv_list[2])
            else:
                depth = float(csv_list[1])
            self.depth = int(depth * 10) / 10
            print(f'Detected depth {self.depth} meters')
        elif str_csv_list_type == "$GPVTG":
            self.speed_over_ground = csv_list[5]
            print(f'Detected speed over ground {self.speed_over_ground} knots')
        elif str_csv_list_type == "$WIMWD":
            self.true_wind_direction = csv_list[1]
            self.true_wind_speed = csv_list[5]
            print(
                f'Detected true wind direction {self.true_wind_direction} degrees (True north) and speed {self.true_wind_speed} knots')
        elif str_csv_list_type == "$WIMWV":
            if self.true_wind_direction != "":
                self.apparent_wind_angle = int(float(csv_list[1]) - float(self.true_wind_direction))
                if self.apparent_wind_angle < 0:
                    self.apparent_wind_angle = -1 * (360 - self.apparent_wind_angle)
            self.apparent_wind_speed = csv_list[3]
            print(
                f'Detected apparent wind angle {self.apparent_wind_angle} degrees and speed {self.apparent_wind_speed} knots')
        elif str_csv_list_type == "$SDVHW":
            self.speed_over_water = csv_list[5]
            print(f'Detected speed over water {self.speed_over_water} knots')

    def write_log_data_to_disk(self):
        while self.disk_write_thread_is_running:
            # Create a log entry and add it to the log entries list
            log_entry = LogEntry(time.gmtime(), time.localtime(), self.heading, self.true_wind_speed, self.true_wind_direction,
                                 self.apparent_wind_speed, self.apparent_wind_angle, self.gps_longitude,
                                 self.gps_latitude, self.gps_elevation, self.water_temperature, self.depth,
                                 self.speed_over_ground, self.speed_over_water)

            # Write log contents to disk
            print("Writing collected data to disk")

            # Append the last added entry to the file on disk
            if self.csv_output:
                with open(f"{self.log_name}.csv", "a") as file:
                    file.write(f'{log_entry}\r\n')

            if self.excel_output:
                # Add the name and price to the sheet
                self.sheet.append(log_entry.string_value_list())

                # Save the workbook
                self.workbook.save(filename=f"{self.log_name}.xlsx")

            if self.gpx_output:
                # Append new GPX track point
                self.gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(log_entry.get_gps_latitude(),
                                                                       log_entry.get_gps_longitude(),
                                                                       elevation=log_entry.gps_elevation))

                # Write the new contents of the GPX file to disk
                with open(f"{self.log_name}.gpx", 'w') as file:
                    file.write(f'{self.gpx.to_xml()}')

            # Sleep for the specified interval
            time.sleep(self.disk_write_interval)

    def end_session(self):
        print("Ending log manager session")
        self.disk_write_thread_is_running = False
