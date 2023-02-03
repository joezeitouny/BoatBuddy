# General
LOG_FILENAME = 'BoatBuddy.log'
LOGGER_NAME = 'BoatBuddy'
LOG_LEVEL = 'DEBUG'  # Log level DEBUG, INFO, WARNING, ERROR, CRITICAL
INITIAL_SNAPSHOT_INTERVAL = 10
DEFAULT_DISK_WRITE_INTERVAL = 900  # Entry disk write interval in seconds (15 minutes = 900 seconds)

# NMEA Plugin
DEFAULT_TCP_PORT = 10110
BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 60

# Victron Plugin
MODBUS_TCP_PORT = 502

# Defaults for command line options
DEFAULT_FILENAME_PREFIX = "Trip_"
DEFAULT_SUMMARY_FILENAME_PREFIX = "Trip_Summary_"
DEFAULT_CSV_OUTPUT_FLAG = False
DEFAULT_EXCEL_OUTPUT_FLAG = False
DEFAULT_GPX_OUTPUT_FLAG = False
DEFAULT_SUMMARY_OUTPUT_FLAG = False
DEFAULT_VERBOSE_FLAG = False
DEFAULT_LIMITED_FLAG = False
