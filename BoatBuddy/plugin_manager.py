import threading
import time
from datetime import datetime
from enum import Enum
from time import mktime

import gpxpy
import gpxpy.gpx
import openpyxl

from BoatBuddy import config
from BoatBuddy import utils
from BoatBuddy.clock_plugin import ClockPlugin
from BoatBuddy.generic_plugin import PluginStatus
from BoatBuddy.nmea_plugin import NMEAPlugin, NMEAPluginEvents
from BoatBuddy.victron_plugin import VictronPlugin, VictronPluginEvents


class PluginManagerStatus(Enum):
    IDLE = 1
    SESSION_ACTIVE = 2


class PluginManager:
    _log_filename = config.DEFAULT_FILENAME_PREFIX
    _output_directory = None
    _time_plugin = None
    _nmea_plugin = None
    _victron_plugin = None
    _workbook = None
    _sheet = None
    _gpx = None
    _gpx_track = None
    _gpx_segment = None
    _summary_filename = config.DEFAULT_SUMMARY_FILENAME_PREFIX
    _timer = None
    _is_session_active = False
    _session_timer = None

    def __init__(self, options, args):
        self._options = options
        self._args = args

        if not self._args[0].endswith('/'):
            self._output_directory = self._args[0] + '/'
        else:
            self._output_directory = self._args[0]

        utils.get_logger().debug('Initializing plugins')

        # initialize the common time plugin
        self._time_plugin = ClockPlugin(self._options)

        if self._options.victron_server_ip:
            # initialize the Victron plugin
            self._victron_plugin = VictronPlugin(self._options)

            if str(self._options.run_mode).lower() == config.SESSION_RUN_MODE_AUTO_VICTRON:
                victron_connection_events = VictronPluginEvents()
                victron_connection_events.on_connect += self._start_session
                victron_connection_events.on_disconnect += self._on_disconnect
                self._victron_plugin.register_for_events(victron_connection_events)

        if self._options.nmea_server_ip:
            # initialize the NMEA0183 plugin
            self._nmea_plugin = NMEAPlugin(self._options)

            if str(self._options.run_mode).lower() == config.SESSION_RUN_MODE_AUTO_NMEA:
                nmea_connection_events = NMEAPluginEvents()
                nmea_connection_events.on_connect += self._start_session
                nmea_connection_events.on_disconnect += self._on_disconnect
                self._nmea_plugin.register_for_events(nmea_connection_events)

        # If normal mode is active then start recording system metrics immediately
        if str(self._options.run_mode).lower() == config.SESSION_RUN_MODE_CONTINUOUS \
                or str(self._options.run_mode).lower() == config.SESSION_RUN_MODE_INTERVAL:
            self._start_session()

            if str(self._options.run_mode).lower() == config.SESSION_RUN_MODE_INTERVAL:
                self._session_timer = threading.Timer(self._options.run_mode_interval, self._session_timer_elapsed)
                self._session_timer.start()

    def _session_timer_elapsed(self):
        # End the current session
        self._end_session()

        # Start a new session
        self._start_session()

        # Restart the session interval timer
        self._session_timer = threading.Timer(self._options.run_mode_interval, self._session_timer_elapsed)
        self._session_timer.start()

    def _write_log_data_to_disk(self):
        # Write contents to disk
        utils.get_logger().info("Writing collected data to disk")

        column_values = []

        self._time_plugin.take_snapshot(store_entry=True)
        column_values += self._time_plugin.get_metadata_values()

        if self._nmea_plugin:
            self._nmea_plugin.take_snapshot(store_entry=True)
            column_values += self._nmea_plugin.get_metadata_values()

        if self._victron_plugin:
            self._victron_plugin.take_snapshot(store_entry=True)
            column_values += self._victron_plugin.get_metadata_values()

        # Append the last added entry to the file on disk
        if self._options.csv:
            with open(f"{self._output_directory}{self._log_filename}.csv", "a") as file:
                file.write(f'{utils.get_comma_separated_string(column_values)}\r\n')

        if self._options.excel:
            # Add the name and price to the sheet
            self._sheet.append(column_values)

            # Save the workbook
            self._workbook.save(filename=f"{self._output_directory}{self._log_filename}.xlsx")

        if self._options.gpx and self._nmea_plugin:
            # If we have valid coordinates then append new GPX track point
            if self._nmea_plugin.is_gps_fix_captured():
                self._gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(latitude=self._nmea_plugin.get_last_latitude_entry(),
                                            longitude=self._nmea_plugin.get_last_longitude_entry(),
                                            time=datetime.fromtimestamp(
                                                mktime(self._time_plugin.get_last_utc_timestamp_entry()))))

                # Write the new contents of the GPX file to disk
                with open(f"{self._output_directory}{self._log_filename}.gpx", 'w') as file:
                    file.write(f'{self._gpx.to_xml()}')

        # Sleep for the specified interval
        self._timer = threading.Timer(self._options.interval, self._write_log_data_to_disk)
        self._timer.start()

    def _start_session(self):
        utils.get_logger().debug('Start collecting system metrics')

        suffix = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        self._log_filename = f'{self._options.filename}{suffix}'
        self._summary_filename = f'{self._options.summary_filename}{suffix}'

        column_headers = self._time_plugin.get_metadata_headers()

        if self._options.nmea_server_ip:
            column_headers += self._nmea_plugin.get_metadata_headers()

        if self._options.victron_server_ip:
            column_headers += self._victron_plugin.get_metadata_headers()

        if self._options.csv:
            # Add the columns headers to the beginning of the csv file
            with open(f"{self._output_directory}{self._log_filename}.csv", "a") as file:
                file.write(f'{utils.get_comma_separated_string(column_headers)}\r\n')

        if self._options.excel:
            # Create an Excel workbook
            self._workbook = openpyxl.Workbook()

            # Create a sheet in the workbook
            self._sheet = self._workbook.active

            # Create the header row
            self._sheet.append(column_headers)

        # Only write to GPX files if the GPX and the NMEA options are both set
        if self._options.gpx and self._options.nmea_server_ip:
            # Creating a new GPX object
            self._gpx = gpxpy.gpx.GPX()

            # Create first track in our GPX:
            self._gpx_track = gpxpy.gpx.GPXTrack()
            self._gpx.tracks.append(self._gpx_track)

            # Create first segment in our GPX track:
            self._gpx_segment = gpxpy.gpx.GPXTrackSegment()
            self._gpx_track.segments.append(self._gpx_segment)

        utils.get_logger().info(f'New session initialized {self._log_filename}')

        self._timer = threading.Timer(config.INITIAL_SNAPSHOT_INTERVAL, self._write_log_data_to_disk)
        self._timer.start()

        self._is_session_active = True

    def _on_disconnect(self):
        # run through this method implementation only if the application is running in auto mode
        if not str(self._options.run_mode).lower() == config.SESSION_RUN_MODE_AUTO_NMEA \
                and not str(self._options.run_mode).lower() == config.SESSION_RUN_MODE_AUTO_VICTRON:
            return

        # End the active session (if any)
        if self._is_session_active:
            self._end_session()

    def _end_session(self):
        # Stop the worker thread timer
        if self._timer:
            self._timer.cancel()

        # if the summary option is set then build a log summary excel workbook
        if self._options.summary:
            # Create an Excel workbook
            summary_workbook = openpyxl.Workbook()

            # Create a sheet in the workbook
            summary_sheet = summary_workbook.active

            # Create the header row
            column_headers = self._time_plugin.get_summary_headers()
            if self._options.nmea_server_ip:
                column_headers += self._nmea_plugin.get_summary_headers()

            if self._options.victron_server_ip:
                column_headers += self._victron_plugin.get_summary_headers()
            summary_sheet.append(column_headers)

            log_summary_list = self._time_plugin.get_summary_values()
            self._time_plugin.reset_entries()

            if self._options.nmea_server_ip:
                log_summary_list += self._nmea_plugin.get_summary_values()
                self._nmea_plugin.reset_entries()

            if self._options.victron_server_ip:
                log_summary_list += self._victron_plugin.get_summary_values()
                self._victron_plugin.reset_entries()

            # Add the name and price to the sheet
            summary_sheet.append(log_summary_list)

            # Save the workbook
            summary_workbook.save(filename=f"{self._output_directory}{self._summary_filename}.xlsx")

        utils.get_logger().info(f'Session {self._log_filename} successfully completed!')

        self._is_session_active = False

    def get_status(self):
        if self._is_session_active:
            return PluginManagerStatus.SESSION_ACTIVE

        return PluginManagerStatus.IDLE

    def finalize(self):
        if self._is_session_active:
            self._end_session()

        if self._session_timer:
            self._session_timer.cancel()

        utils.get_logger().info(f'Waiting for worker threads to finalize...')

        self._time_plugin.finalize()

        if self._options.victron_server_ip:
            self._victron_plugin.finalize()

        if self._options.nmea_server_ip:
            self._nmea_plugin.finalize()

    def get_filtered_nmea_metrics(self) -> {}:
        entry_key_value_list = {}
        entry = self._nmea_plugin.take_snapshot(store_entry=False)
        if entry is not None:
            entry_key_value_list = utils.get_key_value_list(self._nmea_plugin.get_metadata_headers(),
                                                            entry.get_values())
            entry_key_value_list = utils.get_filtered_key_value_list(entry_key_value_list, config.NMEA_METRICS)

        return entry_key_value_list

    def get_filtered_victron_metrics(self) -> {}:
        entry_key_value_list = {}
        entry = self._victron_plugin.take_snapshot(store_entry=False)
        if entry is not None:
            entry_key_value_list = utils.get_key_value_list(self._victron_plugin.get_metadata_headers(),
                                                            entry.get_values())
            entry_key_value_list = utils.get_filtered_key_value_list(entry_key_value_list, config.VICTRON_METRICS)

        return entry_key_value_list

    def get_session_name(self):
        return self._log_filename

    def get_filtered_session_clock_metrics(self):
        return utils.get_filtered_key_value_list(utils.get_key_value_list(self._time_plugin.get_summary_headers(),
                                                                          self._time_plugin.get_summary_values()),
                                                 config.SESSION_HEADER)

    def get_filtered_summary_metrics(self) -> {}:
        summary_key_value_list = {}

        if self._options.nmea_server_ip:
            nmea_dictionary = utils.get_key_value_list(self._nmea_plugin.get_summary_headers(),
                                                       self._nmea_plugin.get_summary_values())
            nmea_dictionary = utils.get_filtered_key_value_list(nmea_dictionary, config.NMEA_SUMMARY)
            summary_key_value_list.update(nmea_dictionary)

        if self._options.victron_server_ip:
            victron_dictionary = utils.get_key_value_list(self._victron_plugin.get_summary_headers(),
                                                          self._victron_plugin.get_summary_values())
            victron_dictionary = utils.get_filtered_key_value_list(victron_dictionary, config.VICTRON_SUMMARY)
            summary_key_value_list.update(victron_dictionary)

        return summary_key_value_list

    def get_victron_plugin_status(self) -> PluginStatus:
        if not self._options.victron_server_ip:
            return PluginStatus.DOWN

        return self._victron_plugin.get_status()

    def get_nmea_plugin_status(self) -> PluginStatus:
        if not self._options.nmea_server_ip:
            return PluginStatus.DOWN

        return self._nmea_plugin.get_status()
