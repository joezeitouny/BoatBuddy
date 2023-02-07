# General
APPLICATION_NAME = 'BoatBuddy'
APPLICATION_VERSION = '0.1.0'
LOG_FILENAME = 'BoatBuddy.log'
LOG_FILE_SIZE = 1024 * 1024  # Log file size 1MB
LOGGER_NAME = 'BoatBuddy'
LOG_LEVEL = 'INFO'  # Log level DEBUG, INFO, WARNING, ERROR, CRITICAL
INITIAL_SNAPSHOT_INTERVAL = 10
DEFAULT_DISK_WRITE_INTERVAL = 900  # Entry disk write interval in seconds (15 minutes = 900 seconds)

# NMEA Plugin
DEFAULT_TCP_PORT = 10110
BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 60

# Victron Plugin
MODBUS_TCP_PORT = 502

# Run modes
RUN_MODE_AUTO = 'auto'
RUN_MODE_MANUAL = 'manual'
RUN_MODE_CONTINUOUS = 'continuous'

# Defaults for command line options
DEFAULT_FILENAME_PREFIX = "Trip_"
DEFAULT_SUMMARY_FILENAME_PREFIX = "Trip_Summary_"
DEFAULT_CSV_OUTPUT_FLAG = False
DEFAULT_EXCEL_OUTPUT_FLAG = False
DEFAULT_GPX_OUTPUT_FLAG = False
DEFAULT_SUMMARY_OUTPUT_FLAG = False
DEFAULT_VERBOSE_FLAG = False
DEFAULT_RUN_MODE = RUN_MODE_CONTINUOUS

# Display filters
SESSION_HEADER = ["Starting Timestamp (UTC)", "Starting Timestamp (Local)", "Duration"]
VICTRON_SUMMARY = ["Housing battery max voltage (V)", "Housing battery min voltage (V)",
                   "Housing battery average voltage (V)", "Housing battery max current (A)",
                   "Housing battery average current (A)", "Housing battery max power (W)",
                   "Housing battery average power (W)",
                   "PV max power (W)", "PV average power",
                   "PV max current (A)", "PV average current (A)",
                   "Starter battery max voltage (V)", "Starter battery min voltage (V)",
                   "Starter battery average voltage",
                   "Tank 1 max level", "Tank 1 min level", "Tank 1 average level",
                   "Tank 2 max level", "Tank 2 min level", "Tank 2 average level"]
NMEA_SUMMARY = ["Starting Location (City, Country)",
                "Starting GPS Latitude (d°m\'S\" H)",
                "Starting GPS Longitude (d°m\'S\" H)", "Ending GPS Latitude (d°m\'S\" H)",
                "Ending GPS Longitude (d°m\'S\" H)", "Distance (miles)", "Heading (degrees)",
                "Average Wind Speed (knots)", "Average Wind Direction (degrees)",
                "Average Water Temperature (°C)", "Average Depth (meters)",
                "Average Speed Over Ground (knots)", "Average Speed Over Water (knots)"]
VICTRON_METRICS = ['Active Input source', 'Grid 1 power (W)', 'Generator 1 power (W)',
                   'AC Input 1 Voltage (V)', 'AC Input 1 Current (A)', 'AC Input 1 Frequency (Hz)',
                   'VE.Bus State', 'AC Consumption (W)', 'Battery Voltage (V)', 'Battery Current (A)',
                   'Battery Power (W)', 'Battery SOC', 'Battery state', 'PV Power (W)', 'PV Current (A)',
                   'Starter Battery Voltage (V)', 'Tank 1 Level (%)', 'Tank 1 Type', 'Tank 2 Level (%)', 'Tank 2 Type']
NMEA_METRICS = ["True Heading (degrees)", "True Wind Speed (knots)",
                "True Wind Direction (degrees)", "Apparent Wind Speed (knots)",
                "Apparent Wind Angle (Relative degrees)", "GPS Longitude (d°m\'S\" H)",
                "GPS Latitude (d°m\'S\" H)", "Water Temperature (°C)",
                "Depth (meters)", "Speed Over Ground (knots)", "Speed Over Water (knots)",
                "Distance From Previous Entry (miles)", "Cumulative Distance (miles)"]
