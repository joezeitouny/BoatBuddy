import optparse
import os
import threading
import time
from datetime import datetime
from time import mktime

import gpxpy
import gpxpy.gpx
import openpyxl

import config
from app import Helper
from app.NMEAPlugin import NMEAPlugin, NMEAPluginEvents
from app.TimePlugin import TimePlugin
from app.VictronPlugin import VictronPlugin

log_filename = config.DEFAULT_FILENAME_PREFIX
output_directory = ''
time_plugin = None
nmea_plugin = None
victron_plugin = None
workbook = None
sheet = None
gpx = None
gpx_track = None
gpx_segment = None
exit_signal = threading.Event()
disk_write_thread = None
summary_filename = config.DEFAULT_SUMMARY_FILENAME_PREFIX
monitoring_in_progress = False
command_line_options = None


def write_log_data_to_disk():
    while not exit_signal.is_set():
        # Write contents to disk
        Helper.console_out("Writing collected data to disk")

        column_values = []

        time_plugin.take_snapshot()
        column_values += time_plugin.get_metadata_values()

        if nmea_plugin:
            nmea_plugin.take_snapshot()
            column_values += nmea_plugin.get_metadata_values()

        if victron_plugin:
            victron_plugin.take_snapshot()
            column_values += victron_plugin.get_metadata_values()

        # Append the last added entry to the file on disk
        if command_line_options.csv:
            with open(f"{output_directory}{log_filename}.csv", "a") as file:
                file.write(f'{Helper.get_comma_separated_string(column_values)}\r\n')

        if command_line_options.excel:
            # Add the name and price to the sheet
            sheet.append(column_values)

            # Save the workbook
            workbook.save(filename=f"{output_directory}{log_filename}.xlsx")

        if command_line_options.gpx:
            # Append new GPX track point
            gpx_segment.points.append(
                gpxpy.gpx.GPXTrackPoint(latitude=nmea_plugin.get_last_latitude_entry(),
                                        longitude=nmea_plugin.get_last_longitude_entry(),
                                        time=datetime.fromtimestamp(
                                            mktime(time_plugin.get_last_utc_timestamp_entry()))))

            # Write the new contents of the GPX file to disk
            with open(f"{output_directory}{log_filename}.gpx", 'w') as file:
                file.write(f'{gpx.to_xml()}')

        # Sleep for the specified interval
        time.sleep(command_line_options.interval)

    Helper.console_out(f'Disk write worker terminated')


def start_disk_helper_thread():
    global disk_write_thread
    disk_write_thread = threading.Thread(target=write_log_data_to_disk)
    disk_write_thread.start()


def initialize_plugins():
    # initialize the common time plugin
    global time_plugin
    time_plugin = TimePlugin(command_line_options)

    if command_line_options.victron_server_ip:
        # initialize the Victron plugin
        global victron_plugin
        victron_plugin = VictronPlugin(command_line_options)

    if command_line_options.nmea_server_ip:
        # initialize the NMEA0183 plugin
        global nmea_plugin
        nmea_plugin = NMEAPlugin(command_line_options)

        if command_line_options.limited:
            limited_mode_events = NMEAPluginEvents()
            limited_mode_events.on_connect += start_monitoring
            limited_mode_events.on_disconnect += stop_monitoring
            nmea_plugin.raise_events(limited_mode_events)


def start_monitoring():
    global exit_signal
    exit_signal = threading.Event()

    suffix = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    global log_filename
    log_filename = f'{command_line_options.filename}{suffix}'
    global summary_filename
    summary_filename = f'{command_line_options.summary_filename}{suffix}'

    column_headers = time_plugin.get_metadata_headers()

    if command_line_options.nmea_server_ip:
        column_headers += nmea_plugin.get_metadata_headers()

    if command_line_options.victron_server_ip:
        column_headers += victron_plugin.get_metadata_headers()

    if command_line_options.csv:
        # Add the columns headers to the beginning of the csv file
        with open(f"{output_directory}{log_filename}.csv", "a") as file:
            file.write(f'{Helper.get_comma_separated_string(column_headers)}\r\n')

    if command_line_options.excel:
        # Create an Excel workbook
        global workbook
        workbook = openpyxl.Workbook()

        # Create a sheet in the workbook
        global sheet
        sheet = workbook.active

        # Create the header row
        sheet.append(column_headers)

    if command_line_options.gpx:
        # Creating a new GPX object
        global gpx
        gpx = gpxpy.gpx.GPX()

        # Create first track in our GPX:
        global gpx_track
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        # Create first segment in our GPX track:
        global gpx_segment
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

    global monitoring_in_progress
    monitoring_in_progress = True

    Helper.console_out(f'New session initialized {log_filename}')

    threading.Timer(command_line_options.interval, start_disk_helper_thread).start()


def finalize_threads():
    Helper.console_out(f'Waiting for worker threads to finalize...')
    # If the thread is running the wait until it finishes
    global disk_write_thread
    if disk_write_thread:
        disk_write_thread.join()

    time_plugin.finalize()

    if command_line_options.nmea_server_ip:
        nmea_plugin.finalize()

    if command_line_options.victron_server_ip:
        victron_plugin.finalize()

    Helper.console_out(f'Worker threads successfully terminated!')


def stop_monitoring():
    global monitoring_in_progress
    if not monitoring_in_progress:
        return

    Helper.console_out(f'Waiting for disk worker thread to finalize...')

    # Send an exit signal to the worker thread
    exit_signal.set()

    # If the thread is running the wait until it finishes
    global disk_write_thread
    if disk_write_thread:
        disk_write_thread.join()

    monitoring_in_progress = False

    end_session()


def end_session():
    # if the summary option is set then build a log summary excel workbook
    if command_line_options.summary:
        # Create an Excel workbook
        summary_workbook = openpyxl.Workbook()

        # Create a sheet in the workbook
        summary_sheet = summary_workbook.active

        # Create the header row
        column_headers = time_plugin.get_summary_headers()
        if command_line_options.nmea_server_ip:
            column_headers += nmea_plugin.get_summary_headers()

        if command_line_options.victron_server_ip:
            column_headers += victron_plugin.get_summary_headers()
        summary_sheet.append(column_headers)

        log_summary_list = time_plugin.get_summary_values()
        time_plugin.reset_entries()

        if command_line_options.nmea_server_ip:
            log_summary_list += nmea_plugin.get_summary_values()
            nmea_plugin.reset_entries()

        if command_line_options.victron_server_ip:
            log_summary_list += victron_plugin.get_summary_values()
            victron_plugin.reset_entries()

        # Add the name and price to the sheet
        summary_sheet.append(log_summary_list)

        # Save the workbook
        summary_workbook.save(filename=f"{output_directory}{summary_filename}.xlsx")

    Helper.console_out(f'Session {log_filename} successfully completed!')


def run(argv):
    # Create an options list using the Options Parser
    parser = optparse.OptionParser()
    parser.set_usage("%prog OUTPUT_DIRECTORY [options]")
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

    global command_line_options
    command_line_options = options

    # If the output directory is not provided
    if len(args) == 0:
        print(f'Error: Output directory is required\r\n')
        parser.print_help()
    elif not os.path.exists(args[0]):
        print(f'Error: Valid output directory is required\r\n')
        parser.print_help()
    elif not command_line_options.excel and not command_line_options.gpx and not command_line_options.csv and not command_line_options.summary:
        print(f'Error: At least one output medium needs to be specified\r\n')
        parser.print_help()
    elif not command_line_options.nmea_server_ip and not command_line_options.victron_server_ip:
        print(f'Error: At least one system metric needs to be specified (NMEA0183, Victron...)\r\n')
        parser.print_help()
    elif command_line_options.limited and not command_line_options.nmea_server_ip:
        print(f'Error: Cannot use the limited mode without providing NMEA0183 configuration parameters\r\n')
        parser.print_help()
    else:
        Helper.verbose_output = command_line_options.verbose
        global output_directory
        if args[0].endswith('/'):
            output_directory = args[0]
        else:
            output_directory = args[0] + '/'
        initialize_plugins()

        if not command_line_options.limited:
            start_monitoring()

        try:
            while True:  # enable children threads to exit the main thread, too
                time.sleep(0.5)  # let it breathe a little
        except KeyboardInterrupt:  # on keyboard interrupt...
            exit_signal.set()  # send signal to all listening threads
            Helper.console_out("Ctrl+C signal detected!")
        finally:
            finalize_threads()
            if not command_line_options.limited:
                end_session()
