import socket
import optparse


from LogManager import LogManager

TCP_PORT = 10110
BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 60
LOG_VERSION = "1.0"
# Disk write interval in seconds
DISK_WRITE_INTERVAL = 5
FILENAME_PREFIX = "Trip_"
EXCEL_OUTPUT = False
CSV_OUTPUT = False
GPX_OUTPUT = False


def dm(x):
    degrees = int(x) // 100
    minutes = x - 100*degrees

    return degrees, minutes


def decimal_degrees(degrees, minutes):
    return degrees + minutes/60


def start_logging(server_ip, server_port, disk_write_interval, filename_prefix, excel, csv, gpx):
    print('Initializing...')

    log_manager = None

    while True:
        print(f'Trying to connect to server with address {server_ip} on port {server_port}...')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(60)

        try:
            client.connect((server_ip, server_port))

            print("Connection established")

            log_manager = LogManager(filename_prefix, disk_write_interval, excel, csv, gpx)

            while True:
                data = client.recv(BUFFER_SIZE)
                if data is None:
                    print('No data received')
                    break

                str_data = data.decode().rstrip('\r\n')

                print(f'Data received: {str_data}')
                LogManager.process_data(log_manager, str_data)

        except TimeoutError:
            print("Connection timeout")
        finally:
            print("Closing connections if any")
            client.close()
            if log_manager is not None:
                log_manager.end_session()


if __name__ == '__main__':
    # Create an options list using the Options Parser
    parser = optparse.OptionParser()
    parser.set_usage("%prog host [options]")
    parser.set_defaults(port=TCP_PORT, filename=FILENAME_PREFIX, interval=DISK_WRITE_INTERVAL,
                        excel=EXCEL_OUTPUT, csv=CSV_OUTPUT, gpx=GPX_OUTPUT)
    parser.add_option('-f', '--file', dest='filename', type='string', help='Output filename prefix. ' +
                                                                           f'Default is {FILENAME_PREFIX}')
    parser.add_option('--excel', action='store_true', dest='excel', help='Generate an Excel workbook. ' +
                                                                         f'Default is {EXCEL_OUTPUT}')
    parser.add_option('--csv', action='store_true', dest='csv', help='Generate a comma separated list (CSV) file. ' +
                                                                     f'Default is {CSV_OUTPUT}')
    parser.add_option('--gpx', action='store_true', dest='gpx', help=f'Generate a GPX file. Default is {GPX_OUTPUT}')
    parser.add_option('--port', dest='port', type='int', help=f'NMEA0183 host port. Default is {TCP_PORT}')
    parser.add_option('-i', '--interval', type='float', dest='interval', help='Disk write interval (in seconds). ' +
                      f'Default is {DISK_WRITE_INTERVAL} seconds')
    (options, args) = parser.parse_args()

    # If the host address is not provided
    if len(args) == 0:
        print(f'Error: Host Address is required\r\n')
        parser.print_help()
    elif not options.excel and not options.gpx and not options.csv:
        print(f'Error: At least one output medium needs to be specified\r\n')
        parser.print_help()
    else:
        start_logging(args[0], options.port, options.interval, options.filename, options.excel,
                      options.csv, options.gpx)
