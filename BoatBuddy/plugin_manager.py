import threading
import time
from datetime import datetime
from enum import Enum
from os.path import exists
from time import mktime

import gpxpy
import gpxpy.gpx
import openpyxl
from events import Events

from BoatBuddy import globals, utils
from BoatBuddy.clock_plugin import ClockPlugin
from BoatBuddy.email_manager import EmailManager
from BoatBuddy.generic_plugin import PluginStatus
from BoatBuddy.gps_plugin import GPSPlugin, GPSPluginEvents
from BoatBuddy.log_manager import LogManager
from BoatBuddy.nmea_plugin import NMEAPlugin, NMEAPluginEvents
from BoatBuddy.notifications_manager import NotificationsManager, NotificationEntryType
from BoatBuddy.sound_manager import SoundManager, SoundType
from BoatBuddy.utils import ModuleStatus
from BoatBuddy.victron_modbus_tcp_plugin import VictronModbusTCPPlugin, VictronModbusTCPPluginEvents
from BoatBuddy.victron_ble_plugin import VictronBLEPlugin


class PluginManagerEvents(Events):
    __events__ = ('on_snapshot', 'on_session_report')


class PluginManagerStatus(Enum):
    IDLE = 'idle'
    SESSION_ACTIVE = 'session_active'


class PluginManager:
    _log_filename = None
    _output_directory = None
    _clock_plugin = None
    _nmea_plugin = None
    _victron_modbus_tcp_plugin = None
    _victron_ble_plugin = None
    _gps_plugin = None
    _workbook = None
    _sheet = None
    _gpx = None
    _gpx_track = None
    _gpx_segment = None
    _summary_filename = None
    _disk_write_timer = None
    _is_session_active = False
    _session_timer = None
    _events = None

    def __init__(self, options, log_manager: LogManager, notifications_manager: NotificationsManager,
                 sound_manager: SoundManager,
                 email_manager: EmailManager):
        self._options = options
        self._log_manager = log_manager
        self._notifications_manager = notifications_manager
        self._sound_manager = sound_manager
        self._email_manager = email_manager

        if not self._options.output_path.endswith('/'):
            self._output_directory = self._options.output_path + '/'
        else:
            self._output_directory = self._options.output_path

        self._log_manager.debug('Initializing plugins')

        # initialize the common time plugin
        self._clock_plugin = ClockPlugin(self._options, self._log_manager)

        if self._options.gps_module:
            self._gps_plugin = GPSPlugin(self._options, self._log_manager)

            gps_connection_events = GPSPluginEvents()
            gps_connection_events.on_connect += self._on_connect_gps_plugin
            gps_connection_events.on_disconnect += self._on_disconnect_gps_plugin
            self._gps_plugin.register_for_events(gps_connection_events)

        if self._options.victron_modbus_tcp_module:
            # initialize the Victron Modbus TCP plugin
            self._victron_modbus_tcp_plugin = VictronModbusTCPPlugin(self._options, self._log_manager)

            victron_modbus_tcp_connection_events = VictronModbusTCPPluginEvents()
            victron_modbus_tcp_connection_events.on_connect += self._on_connect_victron_plugin
            victron_modbus_tcp_connection_events.on_disconnect += self._on_disconnect_victron_plugin
            self._victron_modbus_tcp_plugin.register_for_events(victron_modbus_tcp_connection_events)

        if self._options.victron_ble_module:
            # initialize the Victron BLE plugin
            self._victron_ble_plugin = VictronBLEPlugin(self._options, self._log_manager)

        if self._options.nmea_module:
            # initialize the NMEA0183 plugin
            self._nmea_plugin = NMEAPlugin(self._options, self._log_manager)

            nmea_connection_events = NMEAPluginEvents()
            nmea_connection_events.on_connect += self._on_connect_nmea_plugin
            nmea_connection_events.on_disconnect += self._on_disconnect_nmea_plugin
            self._nmea_plugin.register_for_events(nmea_connection_events)

        # If normal mode is active then start recording system metrics immediately
        if str(self._options.session_run_mode).lower() == globals.SessionRunMode.CONTINUOUS.value \
                or str(self._options.session_run_mode).lower() == globals.SessionRunMode.INTERVAL.value:
            self.start_session()

            if str(self._options.session_run_mode).lower() == globals.SessionRunMode.INTERVAL.value:
                self._session_timer = threading.Timer(self._options.session_paging_interval,
                                                      self._session_timer_elapsed)
                self._session_timer.start()

    def _on_connect_gps_plugin(self):
        self._notifications_manager.notify('gps', ModuleStatus.ONLINE.value, NotificationEntryType.MODULE)
        if str(self._options.session_run_mode).lower() == globals.SessionRunMode.AUTO_GPS.value:
            self.start_session()

    def _on_connect_victron_plugin(self):
        self._notifications_manager.notify('victron', ModuleStatus.ONLINE.value, NotificationEntryType.MODULE)
        if str(self._options.session_run_mode).lower() == globals.SessionRunMode.AUTO_VICTRON.value:
            self.start_session()

    def _on_connect_nmea_plugin(self):
        self._notifications_manager.notify('nmea', ModuleStatus.ONLINE.value, NotificationEntryType.MODULE)
        if str(self._options.session_run_mode).lower() == globals.SessionRunMode.AUTO_NMEA.value:
            self.start_session()

    def _on_disconnect_gps_plugin(self):
        self._notifications_manager.notify('gps', ModuleStatus.OFFLINE.value, NotificationEntryType.MODULE)
        if str(self._options.session_run_mode).lower() == globals.SessionRunMode.AUTO_GPS.value:
            self.end_session()

    def _on_disconnect_victron_plugin(self):
        self._notifications_manager.notify('victron', ModuleStatus.OFFLINE.value, NotificationEntryType.MODULE)
        if str(self._options.session_run_mode).lower() == globals.SessionRunMode.AUTO_VICTRON.value:
            self.end_session()

    def _on_disconnect_nmea_plugin(self):
        self._notifications_manager.notify('nmea', ModuleStatus.OFFLINE.value, NotificationEntryType.MODULE)
        if str(self._options.session_run_mode).lower() == globals.SessionRunMode.AUTO_NMEA.value:
            self.end_session()

    def _session_timer_elapsed(self):
        # End the current session
        self.end_session()

        # Start a new session
        self.start_session()

        # Restart the session interval timer
        self._session_timer = threading.Timer(self._options.session_paging_interval, self._session_timer_elapsed)
        self._session_timer.start()

    def _write_collected_data_to_disk(self):
        # Write contents to disk
        self._log_manager.info("Taking a snapshot and persisting it to disk")

        values = []

        self._clock_plugin.take_snapshot(store_entry=True)
        values += self._clock_plugin.get_metadata_values()

        if self._gps_plugin:
            self._gps_plugin.take_snapshot(store_entry=True)
            values += self._gps_plugin.get_metadata_values()

        if self._nmea_plugin:
            self._nmea_plugin.take_snapshot(store_entry=True)
            values += self._nmea_plugin.get_metadata_values()

        if self._victron_ble_plugin:
            self._victron_ble_plugin.take_snapshot(store_entry=True)
            values += self._victron_ble_plugin.get_metadata_values()

        if self._victron_modbus_tcp_plugin:
            self._victron_modbus_tcp_plugin.take_snapshot(store_entry=True)
            values += self._victron_modbus_tcp_plugin.get_metadata_values()

        # Append the last added entry to the file on disk
        if self._options.csv:
            try:
                with open(f"{self._output_directory}{self._log_filename}.csv", "a") as file:
                    file.write(f'{utils.get_comma_separated_string(values)}\r\n')
            except Exception as e:
                self._log_manager.error(f'Could not write to csv file with filename ' +
                                        f'{self._output_directory}{self._log_filename}.csv. Details: {e}')

        if self._options.excel:
            # Add the name and price to the sheet
            self._sheet.append(values)

            # Save the workbook
            try:
                self._workbook.save(filename=f"{self._output_directory}{self._log_filename}.xlsx")
            except Exception as e:
                self._log_manager.error(f'Could not write to excel file with filename ' +
                                        f'{self._output_directory}{self._log_filename}.xlsx. Details: {e}')

        if self._options.gpx:
            # If we have valid coordinates then append new GPX track point
            if self._nmea_plugin and self._nmea_plugin.is_gps_fix_captured():
                self._gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(latitude=self._nmea_plugin.get_last_latitude_entry(),
                                            longitude=self._nmea_plugin.get_last_longitude_entry(),
                                            time=datetime.fromtimestamp(
                                                mktime(self._clock_plugin.get_last_utc_timestamp_entry()))))

                # Write the new contents of the GPX file to disk
                try:
                    with open(f"{self._output_directory}{self._log_filename}.gpx", 'w') as file:
                        file.write(f'{self._gpx.to_xml()}')
                except Exception as e:
                    self._log_manager.error(f'Could not write to gpx file with filename ' +
                                            f'{self._output_directory}{self._log_filename}.gpx. Details: {e}')
            elif self._gps_plugin and self._gps_plugin.is_gps_fix_captured():
                self._gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(latitude=self._gps_plugin.get_last_latitude_entry(),
                                            longitude=self._gps_plugin.get_last_longitude_entry(),
                                            time=datetime.fromtimestamp(
                                                mktime(self._clock_plugin.get_last_utc_timestamp_entry()))))

                # Write the new contents of the GPX file to disk
                try:
                    with open(f"{self._output_directory}{self._log_filename}.gpx", 'w') as file:
                        file.write(f'{self._gpx.to_xml()}')
                except Exception as e:
                    self._log_manager.error(f'Could not write to gpx file with filename ' +
                                            f'{self._output_directory}{self._log_filename}.gpx. Details: {e}')

        if self._events:
            self._events.on_snapshot(self._log_filename, values)

        # Sleep for the specified interval
        self._disk_write_timer = threading.Timer(self._options.session_disk_write_interval,
                                                 self._write_collected_data_to_disk)
        self._disk_write_timer.start()

    def start_session(self):
        # Play the session started chime
        self._sound_manager.play_sound_async(SoundType.SESSION_STARTED)

        self._log_manager.debug('Start collecting system metrics')

        suffix = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        self._log_filename = f'{self._options.filename_prefix}{suffix}'
        self._summary_filename = f'{self._options.summary_filename_prefix}{suffix}'

        column_headers = self._clock_plugin.get_metadata_headers()

        if self._gps_plugin:
            column_headers += self._gps_plugin.get_metadata_headers()

        if self._nmea_plugin:
            column_headers += self._nmea_plugin.get_metadata_headers()

        if self._victron_ble_plugin:
            column_headers += self._victron_ble_plugin.get_metadata_headers()

        if self._victron_modbus_tcp_plugin:
            column_headers += self._victron_modbus_tcp_plugin.get_metadata_headers()

        if self._options.csv:
            # Add the columns headers to the beginning of the csv file
            try:
                with open(f"{self._output_directory}{self._log_filename}.csv", "a") as file:
                    file.write(f'{utils.get_comma_separated_string(column_headers)}\r\n')
            except Exception as e:
                self._log_manager.error(f'Could not write to csv file with filename ' +
                                        f'{self._output_directory}{self._log_filename}.csv. Details: {e}')

        if self._options.excel:
            # Create an Excel workbook
            self._workbook = openpyxl.Workbook()

            # Create a sheet in the workbook
            self._sheet = self._workbook.active

            # Create the header row
            self._sheet.append(column_headers)

        # Only write to GPX files if the GPX and the NMEA options are both set
        if self._options.gpx and (self._nmea_plugin or self._gps_plugin):
            # Creating a new GPX object
            self._gpx = gpxpy.gpx.GPX()

            # Create first track in our GPX:
            self._gpx_track = gpxpy.gpx.GPXTrack()
            self._gpx.tracks.append(self._gpx_track)

            # Create first segment in our GPX track:
            self._gpx_segment = gpxpy.gpx.GPXTrackSegment()
            self._gpx_track.segments.append(self._gpx_segment)

        self._log_manager.info(f'New session initialized {self._log_filename}')

        self._disk_write_timer = threading.Timer(globals.INITIAL_SNAPSHOT_INTERVAL, self._write_collected_data_to_disk)
        self._disk_write_timer.start()

        self._is_session_active = True

    def end_session(self):
        # If there is no active session then exit
        if not self._is_session_active:
            return

        # Stop the worker thread timer
        if self._disk_write_timer:
            self._disk_write_timer.cancel()

        # Take one last snapshot and persist it to disk
        self._write_collected_data_to_disk()

        # Stop the worker thread timer again
        if self._disk_write_timer:
            self._disk_write_timer.cancel()

        # if the summary option is set then build a log summary excel workbook
        if self._options.session_summary_report:
            # Create an Excel workbook
            summary_workbook = openpyxl.Workbook()

            # Create a sheet in the workbook
            summary_sheet = summary_workbook.active

            # Create the header row
            column_headers = self._clock_plugin.get_summary_headers()

            if self._gps_plugin:
                column_headers += self._gps_plugin.get_summary_headers()

            if self._nmea_plugin:
                column_headers += self._nmea_plugin.get_summary_headers()

            if self._victron_ble_plugin:
                column_headers += self._victron_ble_plugin.get_summary_headers()

            if self._victron_modbus_tcp_plugin:
                column_headers += self._victron_modbus_tcp_plugin.get_summary_headers()
            summary_sheet.append(column_headers)

            log_summary_list = self._clock_plugin.get_summary_values()
            self._clock_plugin.clear_entries()

            if self._gps_plugin:
                log_summary_list += self._gps_plugin.get_summary_values(True)
                self._gps_plugin.clear_entries()

            if self._nmea_plugin:
                log_summary_list += self._nmea_plugin.get_summary_values(True)
                self._nmea_plugin.clear_entries()

            if self._victron_ble_plugin:
                log_summary_list += self._victron_ble_plugin.get_summary_values()
                self._victron_ble_plugin.clear_entries()

            if self._victron_modbus_tcp_plugin:
                log_summary_list += self._victron_modbus_tcp_plugin.get_summary_values()
                self._victron_modbus_tcp_plugin.clear_entries()

            # Add the name and price to the sheet
            summary_sheet.append(log_summary_list)

            # Save the workbook
            try:
                summary_workbook.save(filename=f"{self._output_directory}{self._summary_filename}.xlsx")
            except Exception as e:
                self._log_manager.error(f'Could not write to excel file with filename ' +
                                        f'{self._output_directory}{self._log_filename}.xlsx. Details: {e}')

            if self._events:
                self._events.on_session_report(self._log_filename, log_summary_list)

        self._log_manager.info(f'Session {self._log_filename} successfully completed!')

        self._is_session_active = False

        # Play the session ended chime
        self._sound_manager.play_sound_async(SoundType.SESSION_ENDED)

        # Send a session report if specified
        if self._options.email_session_report:
            try:
                body = f'Please find attached the data files generated from this session.\r\n\r\n' \
                       f'--\r\n{globals.APPLICATION_NAME} ({globals.APPLICATION_VERSION})'
                attachments = []

                if self._options.csv:
                    attachments.append(f"{self._output_directory}{self._log_filename}.csv")

                if self._options.excel:
                    attachments.append(f"{self._output_directory}{self._log_filename}.xlsx")

                if self._options.gpx and (self._nmea_plugin or self._gps_plugin):
                    # Check if the GPX file is generated to cater for the case where no GPS fix was obtained during
                    # the session
                    if exists(f"{self._output_directory}{self._log_filename}.gpx"):
                        attachments.append(f"{self._output_directory}{self._log_filename}.gpx")

                if self._options.session_summary_report:
                    attachments.append(f"{self._output_directory}{self._summary_filename}.xlsx")

                subject = f'{self._options.boat_name} - Session report for session {self._log_filename}'
                self._email_manager.send_email(subject, body, attachments)
                self._log_manager.info(f'Email report for session {self._log_filename} successfully created and '
                                       f'will be sent out shortly')
            except Exception as e:
                self._log_manager.error(f'Error while sending email report for session {self._log_filename}. '
                                        f'Details: {e}')

    def get_status(self):
        if self._is_session_active:
            return PluginManagerStatus.SESSION_ACTIVE

        return PluginManagerStatus.IDLE

    def finalize(self):
        self.end_session()

        if self._session_timer:
            self._session_timer.cancel()

        self._log_manager.info(f'Waiting for worker threads to finalize...')

        self._clock_plugin.finalize()

        if self._gps_plugin:
            self._gps_plugin.finalize()

        if self._victron_ble_plugin:
            self._victron_ble_plugin.finalize()

        if self._victron_modbus_tcp_plugin:
            self._victron_modbus_tcp_plugin.finalize()

        if self._nmea_plugin:
            self._nmea_plugin.finalize()

    def get_clock_metrics(self) -> {}:
        entry = self._clock_plugin.take_snapshot(store_entry=False)
        if entry is not None:
            return entry.get_values()

        return []

    def get_nmea_plugin_metrics(self) -> {}:
        entry = self._nmea_plugin.take_snapshot(store_entry=False)
        if entry is not None:
            return entry.get_values()

        return []

    def get_victron_ble_plugin_metrics(self) -> {}:
        entry = self._victron_ble_plugin.take_snapshot(store_entry=False)
        if entry is not None:
            return entry.get_values()

        return []

    def get_victron_modbus_tcp_plugin_metrics(self) -> {}:
        entry = self._victron_modbus_tcp_plugin.take_snapshot(store_entry=False)
        if entry is not None:
            return entry.get_values()

        return []

    def get_gps_plugin_metrics(self) -> {}:
        entry = self._gps_plugin.take_snapshot(store_entry=False)
        if entry is not None:
            return entry.get_values()

        return []

    def get_session_name(self):
        return self._log_filename

    def get_session_clock_metrics(self):
        return utils.get_key_value_list(self._clock_plugin.get_summary_headers(),
                                        self._clock_plugin.get_summary_values())

    def get_session_summary_metrics(self) -> {}:
        summary_key_value_list = {}

        if self._gps_plugin:
            gps_dictionary = utils.get_key_value_list(self._gps_plugin.get_summary_headers(),
                                                      self._gps_plugin.get_summary_values())
            summary_key_value_list.update(gps_dictionary)

        if self._nmea_plugin:
            nmea_dictionary = utils.get_key_value_list(self._nmea_plugin.get_summary_headers(),
                                                       self._nmea_plugin.get_summary_values())
            summary_key_value_list.update(nmea_dictionary)

        if self._victron_ble_plugin:
            victron_ble_dictionary = utils.get_key_value_list(self._victron_ble_plugin.get_summary_headers(),
                                                              self._victron_ble_plugin.get_summary_values())
            summary_key_value_list.update(victron_ble_dictionary)

        if self._victron_modbus_tcp_plugin:
            victron_modbus_tcp_dictionary = utils.get_key_value_list(
                self._victron_modbus_tcp_plugin.get_summary_headers(),
                self._victron_modbus_tcp_plugin.get_summary_values())
            summary_key_value_list.update(victron_modbus_tcp_dictionary)

        return summary_key_value_list

    def get_victron_ble_plugin_status(self) -> PluginStatus:
        if not self._victron_ble_plugin:
            return PluginStatus.DOWN

        return self._victron_ble_plugin.get_status()

    def get_victron_modbus_tcp_plugin_status(self) -> PluginStatus:
        if not self._victron_modbus_tcp_plugin:
            return PluginStatus.DOWN

        return self._victron_modbus_tcp_plugin.get_status()

    def get_nmea_plugin_status(self) -> PluginStatus:
        if not self._nmea_plugin:
            return PluginStatus.DOWN

        return self._nmea_plugin.get_status()

    def get_gps_plugin_status(self) -> PluginStatus:
        if not self._gps_plugin:
            return PluginStatus.DOWN

        return self._gps_plugin.get_status()

    def get_gps_plugin_accuracy(self):
        if not self._gps_plugin:
            return 'N/A'

        return self._gps_plugin.get_accuracy()

    def register_for_events(self, events):
        self._events = events
