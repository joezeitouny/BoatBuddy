import optparse
import threading
import time
from datetime import datetime
from time import mktime

import gpxpy
import gpxpy.gpx
import openpyxl

import Helper
from NMEAPlugin import NMEAPlugin
from VictronPlugin import VictronPlugin

DEFAULT_TCP_PORT = 10110
DEFAULT_BUFFER_SIZE = 4096
DEFAULT_SOCKET_TIMEOUT = 60
DEFAULT_DISK_WRITE_INTERVAL = 5
DEFAULT_FILENAME_PREFIX = "Trip_"
DEFAULT_CSV_OUTPUT_FLAG = False
DEFAULT_EXCEL_OUTPUT_FLAG = False
DEFAULT_GPX_OUTPUT_FLAG = False
DEFAULT_SUMMARY_OUTPUT_FLAG = False
DEFAULT_SUMMARY_FILENAME_PREFIX = "Trip_Summary_"
DEFAULT_VERBOSE_FLAG = False

log_filename = DEFAULT_FILENAME_PREFIX
nmea_plugin = None
victron_plugin = None
workbook = None
sheet = None
gpx = None
gpx_track = None
gpx_segment = None
exit_signal = threading.Event()
disk_write_thread = None
summary_filename = DEFAULT_SUMMARY_FILENAME_PREFIX


def write_log_data_to_disk():
    while not exit_signal.is_set():
        # Write contents to disk
        Helper.console_out("Writing collected data to disk")

        column_values = []

        if nmea_plugin:
            nmea_plugin.take_snapshot()
            column_values += nmea_plugin.get_metadata_values()

        if victron_plugin:
            victron_plugin.take_snapshot()
            column_values += victron_plugin.get_metadata_values()

        # Append the last added entry to the file on disk
        if options.csv:
            with open(f"{log_filename}.csv", "a") as file:
                file.write(f'{Helper.get_comma_separated_string(column_values)}\r\n')

        if options.excel:
            # Add the name and price to the sheet
            sheet.append(column_values)

            # Save the workbook
            workbook.save(filename=f"{log_filename}.xlsx")

        if options.gpx:
            # Append new GPX track point
            gpx_segment.points.append(
                gpxpy.gpx.GPXTrackPoint(latitude=nmea_plugin.get_last_latitude_entry(),
                                        longitude=nmea_plugin.get_last_longitude_entry(),
                                        time=datetime.fromtimestamp(
                                            mktime(nmea_plugin.get_last_utc_timestamp_entry()))))

            # Write the new contents of the GPX file to disk
            with open(f"{log_filename}.gpx", 'w') as file:
                file.write(f'{gpx.to_xml()}')

        # Sleep for the specified interval
        time.sleep(options.interval)

    Helper.console_out(f'Disk write worker terminated')


def start_disk_helper_thread():
    global disk_write_thread
    disk_write_thread = threading.Thread(target=write_log_data_to_disk)
    disk_write_thread.start()


def initialize_plugins():
    if options.victron_server_ip:
        # initialize the Victron plugin
        global victron_plugin
        victron_plugin = VictronPlugin(options)

    if options.nmea_server_ip:
        # initialize the NMEA0183 plugin
        global nmea_plugin
        nmea_plugin = NMEAPlugin(options)


def start_monitoring():
    suffix = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    global log_filename
    log_filename = f'{options.filename}{suffix}'
    global summary_filename
    summary_filename = f'{options.summary_filename}{suffix}'

    column_headers = []
    if options.nmea_server_ip:
        column_headers += nmea_plugin.get_metadata_headers()

    if options.victron_server_ip:
        column_headers += victron_plugin.get_metadata_headers()

    if options.csv:
        # Add the columns headers to the beginning of the csv file
        with open(f"{log_filename}.csv", "a") as file:
            file.write(f'{Helper.get_comma_separated_string(column_headers)}\r\n')

    if options.excel:
        # Create an Excel workbook
        global workbook
        workbook = openpyxl.Workbook()

        # Create a sheet in the workbook
        global sheet
        sheet = workbook.active

        # Create the header row
        sheet.append(column_headers)

    if options.gpx:
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

    Helper.console_out(f'New session initialized {log_filename}')

    threading.Timer(options.interval, start_disk_helper_thread).start()


def finalize_threads():
    Helper.console_out(f'Waiting for worker threads to finalize...')
    # If the thread is running the wait until it finishes
    global disk_write_thread
    if disk_write_thread:
        disk_write_thread.join()

    if options.nmea_server_ip:
        nmea_plugin.finalize()

    if options.victron_server_ip:
        victron_plugin.finalize()

    Helper.console_out(f'Worker threads successfully terminated!')


def end_session():
    # if the summary option is set then build a log summary excel workbook
    if options.summary:
        # Create an Excel workbook
        summary_workbook = openpyxl.Workbook()

        # Create a sheet in the workbook
        summary_sheet = summary_workbook.active

        # Create the header row
        column_headers = []
        if options.nmea_server_ip:
            column_headers += nmea_plugin.get_summary_headers()

        if options.victron_server_ip:
            column_headers += victron_plugin.get_summary_headers()
        summary_sheet.append(column_headers)

        log_summary_list = []

        if options.nmea_server_ip:
            log_summary_list += nmea_plugin.get_summary_values()
            nmea_plugin.reset_entries()

        if options.victron_server_ip:
            log_summary_list += victron_plugin.get_summary_values()
            victron_plugin.reset_entries()

        # Add the name and price to the sheet
        summary_sheet.append(log_summary_list)

        # Save the workbook
        summary_workbook.save(filename=f"{summary_filename}.xlsx")

    Helper.console_out(f'Session {log_filename} successfully completed!')


if __name__ == '__main__':
    # Create an options list using the Options Parser
    parser = optparse.OptionParser()
    parser.set_usage("%prog [options]")
    parser.set_defaults(nmea_port=DEFAULT_TCP_PORT, filename=DEFAULT_FILENAME_PREFIX,
                        interval=DEFAULT_DISK_WRITE_INTERVAL, excel=DEFAULT_EXCEL_OUTPUT_FLAG,
                        csv=DEFAULT_CSV_OUTPUT_FLAG, gpx=DEFAULT_GPX_OUTPUT_FLAG,
                        summary=DEFAULT_SUMMARY_OUTPUT_FLAG, summary_filename=DEFAULT_SUMMARY_FILENAME_PREFIX,
                        verbose=DEFAULT_VERBOSE_FLAG)
    parser.add_option('--nmea-server-ip', dest='nmea_server_ip', type='string',
                      help=f'Append NMEA0183 network metrics from the specified device IP')
    parser.add_option('--nmea-server-port', dest='nmea_port', type='int', help=f'NMEA0183 host port. ' +
                                                                               f'Default is: {DEFAULT_TCP_PORT}')
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
    if not options.excel and not options.gpx and not options.csv and not options.summary:
        print(f'Error: At least one output medium needs to be specified\r\n')
        parser.print_help()
    elif not options.nmea_server_ip and not options.victron_server_ip:
        print(f'Error: At least one system metric needs to be specified (NMEA0183, Victron...)\r\n')
        parser.print_help()
    else:
        Helper.verbose_output = options.verbose
        initialize_plugins()
        start_monitoring()

        try:
            while not exit_signal.is_set():  # enable children threads to exit the main thread, too
                time.sleep(0.1)  # let it breathe a little
        except KeyboardInterrupt:  # on keyboard interrupt...
            exit_signal.set()  # send signal to all listening threads
            Helper.console_out("Ctrl+C signal detected!")
        finally:
            finalize_threads()
            end_session()
