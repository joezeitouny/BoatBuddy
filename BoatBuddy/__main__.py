import logging
import optparse
import os
import threading
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from time import mktime

import gpxpy
import gpxpy.gpx
import openpyxl

from BoatBuddy import config
from BoatBuddy import utils
from BoatBuddy.clock_plugin import ClockPlugin
from BoatBuddy.nmea_plugin import NMEAPlugin, NMEAPluginEvents
from BoatBuddy.victron_plugin import VictronPlugin

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


def _write_log_data_to_disk():
    # Write contents to disk
    utils.get_logger().info("Writing collected data to disk")

    column_values = []

    _time_plugin.take_snapshot()
    column_values += _time_plugin.get_metadata_values()

    if _nmea_plugin:
        _nmea_plugin.take_snapshot()
        column_values += _nmea_plugin.get_metadata_values()

    if _victron_plugin:
        _victron_plugin.take_snapshot()
        column_values += _victron_plugin.get_metadata_values()

    # Append the last added entry to the file on disk
    if options.csv:
        with open(f"{_output_directory}{_log_filename}.csv", "a") as file:
            file.write(f'{utils.get_comma_separated_string(column_values)}\r\n')

    if options.excel:
        # Add the name and price to the sheet
        _sheet.append(column_values)

        # Save the workbook
        _workbook.save(filename=f"{_output_directory}{_log_filename}.xlsx")

    if options.gpx and _nmea_plugin:
        # If we have valid coordinates then append new GPX track point
        if _nmea_plugin.is_gps_fix_captured():
            _gpx_segment.points.append(
                gpxpy.gpx.GPXTrackPoint(latitude=_nmea_plugin.get_last_latitude_entry(),
                                        longitude=_nmea_plugin.get_last_longitude_entry(),
                                        time=datetime.fromtimestamp(
                                            mktime(_time_plugin.get_last_utc_timestamp_entry()))))

            # Write the new contents of the GPX file to disk
            with open(f"{_output_directory}{_log_filename}.gpx", 'w') as file:
                file.write(f'{_gpx.to_xml()}')

    # Sleep for the specified interval
    global _timer
    _timer = threading.Timer(options.interval, _write_log_data_to_disk)
    _timer.start()


def _initialize():
    utils.get_logger().debug('Initializing plugins')

    global _output_directory
    if not args[0].endswith('/'):
        _output_directory = args[0] + '/'
    else:
        _output_directory = args[0]

    # initialize the common time plugin
    global _time_plugin
    _time_plugin = ClockPlugin(options)

    if options.victron_server_ip:
        # initialize the Victron plugin
        global _victron_plugin
        _victron_plugin = VictronPlugin(options)

    if options.nmea_server_ip:
        # initialize the NMEA0183 plugin
        global _nmea_plugin
        _nmea_plugin = NMEAPlugin(options)

        if options.limited:
            limited_mode_events = NMEAPluginEvents()
            limited_mode_events.on_connect += _start_collecting_metrics
            limited_mode_events.on_disconnect += _on_nmea_server_disconnect
            _nmea_plugin.register_for_events(limited_mode_events)


def _start_collecting_metrics():
    utils.get_logger().debug('Start collecting system metrics')

    suffix = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    global _log_filename
    _log_filename = f'{options.filename}{suffix}'
    global _summary_filename
    _summary_filename = f'{options.summary_filename}{suffix}'

    column_headers = _time_plugin.get_metadata_headers()

    if options.nmea_server_ip:
        column_headers += _nmea_plugin.get_metadata_headers()

    if options.victron_server_ip:
        column_headers += _victron_plugin.get_metadata_headers()

    if options.csv:
        # Add the columns headers to the beginning of the csv file
        with open(f"{_output_directory}{_log_filename}.csv", "a") as file:
            file.write(f'{utils.get_comma_separated_string(column_headers)}\r\n')

    if options.excel:
        # Create an Excel workbook
        global _workbook
        _workbook = openpyxl.Workbook()

        # Create a sheet in the workbook
        global _sheet
        _sheet = _workbook.active

        # Create the header row
        _sheet.append(column_headers)

    # Only write to GPX files if the GPX and the NMEA options are both set
    if options.gpx and options.nmea_server_ip:
        # Creating a new GPX object
        global _gpx
        _gpx = gpxpy.gpx.GPX()

        # Create first track in our GPX:
        global _gpx_track
        _gpx_track = gpxpy.gpx.GPXTrack()
        _gpx.tracks.append(_gpx_track)

        # Create first segment in our GPX track:
        global _gpx_segment
        _gpx_segment = gpxpy.gpx.GPXTrackSegment()
        _gpx_track.segments.append(_gpx_segment)

    utils.get_logger().info(f'New session initialized {_log_filename}')

    global _timer
    _timer = threading.Timer(config.INITIAL_SNAPSHOT_INTERVAL, _write_log_data_to_disk)
    _timer.start()

    global _is_session_active
    _is_session_active = True


def _prepare_to_shutdown():
    utils.get_logger().info(f'Waiting for worker threads to finalize...')
    # If the thread is running the wait until it finishes
    if _timer:
        _timer.cancel()
    utils.get_logger().info(f'Disk write worker terminated')

    _time_plugin.finalize()

    if options.victron_server_ip:
        _victron_plugin.finalize()

    if options.nmea_server_ip:
        _nmea_plugin.finalize()


def _on_nmea_server_disconnect():
    # run through this method implementation only if the application is running in limited mode
    if not options.limited:
        return

    _prepare_to_shutdown()

    global _is_session_active
    if _is_session_active:
        _end_session()
    # Re-initialize the system components to reset the state of the system
    _initialize()


def _end_session():
    # if the summary option is set then build a log summary excel workbook
    if options.summary:
        # Create an Excel workbook
        summary_workbook = openpyxl.Workbook()

        # Create a sheet in the workbook
        summary_sheet = summary_workbook.active

        # Create the header row
        column_headers = _time_plugin.get_summary_headers()
        if options.nmea_server_ip:
            column_headers += _nmea_plugin.get_summary_headers()

        if options.victron_server_ip:
            column_headers += _victron_plugin.get_summary_headers()
        summary_sheet.append(column_headers)

        log_summary_list = _time_plugin.get_summary_values()
        _time_plugin.reset_entries()

        if options.nmea_server_ip:
            log_summary_list += _nmea_plugin.get_summary_values()
            _nmea_plugin.reset_entries()

        if options.victron_server_ip:
            log_summary_list += _victron_plugin.get_summary_values()
            _victron_plugin.reset_entries()

        # Add the name and price to the sheet
        summary_sheet.append(log_summary_list)

        # Save the workbook
        summary_workbook.save(filename=f"{_output_directory}{_summary_filename}.xlsx")

    utils.get_logger().info(f'Session {_log_filename} successfully completed!')

    global _is_session_active
    _is_session_active = False


if __name__ == '__main__':
    # Create an options list using the Options Parser
    parser = optparse.OptionParser()
    parser.set_usage("python3 -m BoatBuddy OUTPUT_DIRECTORY [options]")
    parser.set_defaults(nmea_port=config.DEFAULT_TCP_PORT, filename=config.DEFAULT_FILENAME_PREFIX,
                        interval=config.DEFAULT_DISK_WRITE_INTERVAL, excel=config.DEFAULT_EXCEL_OUTPUT_FLAG,
                        csv=config.DEFAULT_CSV_OUTPUT_FLAG, gpx=config.DEFAULT_GPX_OUTPUT_FLAG,
                        summary=config.DEFAULT_SUMMARY_OUTPUT_FLAG,
                        summary_filename=config.DEFAULT_SUMMARY_FILENAME_PREFIX,
                        verbose=config.DEFAULT_VERBOSE_FLAG, limited=config.DEFAULT_LIMITED_FLAG,
                        log=config.LOG_LEVEL)
    parser.add_option('--nmea-server-ip', dest='nmea_server_ip', type='string',
                      help=f'Append NMEA0183 network metrics from the specified device IP')
    parser.add_option('--nmea-server-port', dest='nmea_port', type='int', help=f'NMEA0183 host port. ' +
                                                                               f'Default is: {config.DEFAULT_TCP_PORT}')
    parser.add_option('-i', '--interval', type='float', dest='interval',
                      help=f'Disk write interval (in seconds). Default is: ' +
                           f'{config.DEFAULT_DISK_WRITE_INTERVAL} seconds')
    parser.add_option('--excel', action='store_true', dest='excel', help='Generate an Excel workbook.')
    parser.add_option('--csv', action='store_true', dest='csv', help='Generate a comma separated list (CSV) file.')
    parser.add_option('--gpx', action='store_true', dest='gpx', help=f'Generate a GPX file.')
    parser.add_option('-f', '--file', dest='filename', type='string',
                      help=f'Output filename prefix. Default is: {config.DEFAULT_FILENAME_PREFIX}')
    parser.add_option('--summary', action='store_true', dest='summary',
                      help=f'Generate a trip summary excel workbook at the end of the session.')
    parser.add_option('--summary-filename-prefix', dest='summary_filename', type='string',
                      help=f'Summary filename prefix. Default is: {config.DEFAULT_SUMMARY_FILENAME_PREFIX}')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                      help=f'Verbose mode. Print debugging messages about captured data. ' +
                           f'This is helpful in debugging connection, and configuration problems.')
    parser.add_option('--victron-server-ip', dest='victron_server_ip', type='string',
                      help=f'Append Victron system metrics from the specified device IP')
    parser.add_option('--limited-mode', action='store_true', dest='limited',
                      help=f'Sessions are only initialized when the NMEA server is up')
    parser.add_option('--log', dest='log', type='string',
                      help=f'Desired log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    (options, args) = parser.parse_args()

    log_numeric_level = getattr(logging, options.log.upper(), None)
    if not isinstance(log_numeric_level, int):
        print(f'Invalid argument: Log level "{options.log}"')
        parser.print_help()
    elif len(args) == 0:  # If the output directory is not provided
        print(f'Invalid argument: Output directory is required\r\n')
        parser.print_help()
    elif not os.path.exists(args[0]):
        print(f'Invalid argument: Valid output directory is required\r\n')
        parser.print_help()
    elif not options.excel and not options.gpx and not options.csv and not options.summary:
        print(f'Invalid argument: At least one output medium needs to be specified\r\n')
        parser.print_help()
    elif not options.nmea_server_ip and not options.victron_server_ip:
        print(f'Invalid argument: At least one system metric needs to be specified (NMEA0183, Victron...)\r\n')
        parser.print_help()
    elif options.limited and not options.nmea_server_ip:
        print(f'Invalid argument: Cannot use the limited mode without providing NMEA0183 configuration parameters\r\n')
        parser.print_help()
    elif options.interval < config.INITIAL_SNAPSHOT_INTERVAL:
        print(f'Invalid argument: Specified disk write interval cannot be less than ' +
              f'{config.INITIAL_SNAPSHOT_INTERVAL} seconds')
    else:
        if options.verbose:
            # Initialize the logging module
            log_filename = ''
            if not args[0].endswith('/'):
                log_filename = args[0] + '/' + config.LOG_FILENAME
            else:
                log_filename = args[0] + config.LOG_FILENAME

            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
            # Limit log file size
            file_handler = RotatingFileHandler(log_filename, encoding='utf-8', maxBytes=config.LOG_FILE_SIZE,
                                               backupCount=1)
            file_handler.setFormatter(formatter)
            logging.getLogger(config.LOGGER_NAME).setLevel(log_numeric_level)
            logging.getLogger(config.LOGGER_NAME).addHandler(file_handler)
        else:
            logging.getLogger(config.LOGGER_NAME).disabled = True

        _initialize()

        # If normal mode is active then start recording system metrics immediately
        if not options.limited:
            _start_collecting_metrics()

        try:
            while True:  # enable children threads to exit the main thread, too
                time.sleep(0.5)  # let it breathe a little
        except KeyboardInterrupt:  # on keyboard interrupt...
            utils.get_logger().warning("Ctrl+C signal detected!")
        finally:
            _prepare_to_shutdown()
            if _is_session_active:
                _end_session()
