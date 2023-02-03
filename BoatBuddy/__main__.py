import optparse
import os
import threading
import time
from datetime import datetime
from time import mktime

import gpxpy
import gpxpy.gpx
import openpyxl

from BoatBuddy import config
from BoatBuddy import utils
from BoatBuddy.clock_plugin import TimePlugin
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
_exit_signal = threading.Event()
_disk_write_thread = None
_summary_filename = config.DEFAULT_SUMMARY_FILENAME_PREFIX
_monitoring_in_progress = False


def write_log_data_to_disk():
    while not _exit_signal.is_set():
        # Write contents to disk
        utils.console_out("Writing collected data to disk")

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

        if options.gpx:
            # Append new GPX track point
            _gpx_segment.points.append(
                gpxpy.gpx.GPXTrackPoint(latitude=_nmea_plugin.get_last_latitude_entry(),
                                        longitude=_nmea_plugin.get_last_longitude_entry(),
                                        time=datetime.fromtimestamp(
                                            mktime(_time_plugin.get_last_utc_timestamp_entry()))))

            # Write the new contents of the GPX file to disk
            with open(f"{_output_directory}{_log_filename}.gpx", 'w') as file:
                file.write(f'{_gpx.to_xml()}')

        # Sleep for the specified interval
        time.sleep(options.interval)

    utils.console_out(f'Disk write worker terminated')


def start_disk_helper_thread():
    global _disk_write_thread
    _disk_write_thread = threading.Thread(target=write_log_data_to_disk)
    _disk_write_thread.start()


def initialize():
    global _output_directory
    if not args[0].endswith('/'):
        _output_directory = args[0] + '/'
    else:
        _output_directory = args[0]

    # initialize the common time plugin
    global _time_plugin
    _time_plugin = TimePlugin(options)

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
            limited_mode_events.on_connect += start_monitoring
            limited_mode_events.on_disconnect += stop_monitoring
            _nmea_plugin.raise_events(limited_mode_events)


def start_monitoring():
    global _exit_signal
    _exit_signal = threading.Event()

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

    if options.gpx:
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

    global _monitoring_in_progress
    _monitoring_in_progress = True

    utils.console_out(f'New session initialized {_log_filename}')

    threading.Timer(options.interval, start_disk_helper_thread).start()


def finalize_threads():
    utils.console_out(f'Waiting for worker threads to finalize...')
    # If the thread is running the wait until it finishes
    global _disk_write_thread
    if _disk_write_thread:
        _disk_write_thread.join()

    _time_plugin.finalize()

    if options.nmea_server_ip:
        _nmea_plugin.finalize()

    if options.victron_server_ip:
        _victron_plugin.finalize()

    utils.console_out(f'Worker threads successfully terminated!')


def stop_monitoring():
    global _monitoring_in_progress
    if not _monitoring_in_progress:
        return

    utils.console_out(f'Waiting for disk worker thread to finalize...')

    # Send an exit signal to the worker thread
    _exit_signal.set()

    # If the thread is running the wait until it finishes
    global _disk_write_thread
    if _disk_write_thread:
        _disk_write_thread.join()

    _monitoring_in_progress = False

    end_session()


def end_session():
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

    utils.console_out(f'Session {_log_filename} successfully completed!')


if __name__ == '__main__':
    # Create an options list using the Options Parser
    parser = optparse.OptionParser()
    parser.set_usage("python3 -m BoatBuddy OUTPUT_DIRECTORY [options]")
    parser.set_defaults(nmea_port=config.DEFAULT_TCP_PORT, filename=config.DEFAULT_FILENAME_PREFIX,
                        interval=config.DEFAULT_DISK_WRITE_INTERVAL, excel=config.DEFAULT_EXCEL_OUTPUT_FLAG,
                        csv=config.DEFAULT_CSV_OUTPUT_FLAG, gpx=config.DEFAULT_GPX_OUTPUT_FLAG,
                        summary=config.DEFAULT_SUMMARY_OUTPUT_FLAG,
                        summary_filename=config.DEFAULT_SUMMARY_FILENAME_PREFIX,
                        verbose=config.DEFAULT_VERBOSE_FLAG, limited=config.DEFAULT_LIMITED_FLAG)
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
                      help='Output filename prefix. Default is: {config.DEFAULT_FILENAME_PREFIX}')
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
    (options, args) = parser.parse_args()

    # If the output directory is not provided
    if len(args) == 0:
        print(f'Error: Output directory is required\r\n')
        parser.print_help()
    elif not os.path.exists(args[0]):
        print(f'Error: Valid output directory is required\r\n')
        parser.print_help()
    elif not options.excel and not options.gpx and not options.csv and not options.summary:
        print(f'Error: At least one output medium needs to be specified\r\n')
        parser.print_help()
    elif not options.nmea_server_ip and not options.victron_server_ip:
        print(f'Error: At least one system metric needs to be specified (NMEA0183, Victron...)\r\n')
        parser.print_help()
    elif options.limited and not options.nmea_server_ip:
        print(f'Error: Cannot use the limited mode without providing NMEA0183 configuration parameters\r\n')
        parser.print_help()
    else:
        utils._verbose_output = options.verbose

        initialize()

        if not options.limited:
            start_monitoring()

        try:
            while True:  # enable children threads to exit the main thread, too
                time.sleep(0.5)  # let it breathe a little
        except KeyboardInterrupt:  # on keyboard interrupt...
            _exit_signal.set()  # send signal to all listening threads
            utils.console_out("Ctrl+C signal detected!")
        finally:
            finalize_threads()
            if not options.limited:
                end_session()
