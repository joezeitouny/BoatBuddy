# General
APPLICATION_NAME = 'Boat Buddy'
APPLICATION_VERSION = '0.2.6'
LOG_FILENAME = 'BoatBuddy.log'
LOG_FILE_SIZE = 1024 * 1024  # Log file size 1MB
LOGGER_NAME = 'BoatBuddy'
LOG_LEVEL = 'INFO'  # Log level DEBUG, INFO, WARNING, ERROR, CRITICAL
INITIAL_SNAPSHOT_INTERVAL = 10  # Time to wait for the first snapshot to be taken after the session starts in seconds
DEFAULT_DISK_WRITE_INTERVAL = 900  # Entry disk write interval in seconds (15 minutes = 900 seconds)

# NMEA Plugin
DEFAULT_TCP_PORT = 10110
BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 60
NMEA_TIMER_INTERVAL = 1  # In seconds, defines the amount of time to wait between metrics retrievals

# Victron Plugin
MODBUS_TCP_PORT = 502
VICTRON_TIMER_INTERVAL = 1  # In seconds, defines the amount of time to wait between metrics retrievals

# Run modes
SESSION_RUN_MODE_AUTO_NMEA = 'auto-nmea'
SESSION_RUN_MODE_AUTO_VICTRON = 'auto-victron'
SESSION_RUN_MODE_CONTINUOUS = 'continuous'
SESSION_RUN_MODE_INTERVAL = 'interval'

# Defaults for command line options
DEFAULT_FILENAME_PREFIX = 'Trip_'
DEFAULT_SUMMARY_FILENAME_PREFIX = 'Trip_Summary_'
DEFAULT_CSV_OUTPUT_FLAG = False
DEFAULT_EXCEL_OUTPUT_FLAG = False
DEFAULT_GPX_OUTPUT_FLAG = False
DEFAULT_SUMMARY_OUTPUT_FLAG = False
DEFAULT_VERBOSE_FLAG = False
DEFAULT_SESSION_RUN_MODE = SESSION_RUN_MODE_CONTINUOUS
# Time in seconds between each session is finalized when running in interval mode
DEFAULT_SESSION_INTERVAL = 60 * 60 * 24  # default is every 24h

# Display colouring template
COLOURING_SCHEME = {'Tank 1 Level (%)': {'yellow': [60, 80], 'green': [80, 100], 'red': [0, 60]},
                    'Tank 2 Level (%)': {'yellow': [60, 80], 'green': [80, 100], 'red': [0, 60]},
                    'Battery SOC': {'yellow': [60, 80], 'green': [80, 100], 'red': [0, 60]},
                    'Battery Voltage (V)': {'yellow': [12.6, 12.8], 'green': [12.8, 15], 'red': [0, 12.6]},
                    'Starter Battery Voltage (V)': {'yellow': [12.6, 12.8], 'green': [12.8, 15], 'red': [0, 12.6]},
                    'True Wind Speed (knots)': {'yellow': [15, 20], 'green': [0, 15], 'red': [20, 100]},
                    'Apparent Wind Speed (knots)': {'yellow': [15, 20], 'green': [0, 15], 'red': [20, 100]},
                    'Depth (meters)': {'yellow': [4, 20], 'green': [20, 400], 'red': [0, 4]}}

# Display filters
SESSION_HEADER = ['Starting Time (UTC)', 'Starting Time (Local)', 'Duration']
VICTRON_SUMMARY = ['Housing battery max voltage (V)', 'Housing battery min voltage (V)',
                   'Housing battery average voltage (V)', 'Housing battery max current (A)',
                   'Housing battery average current (A)', 'Housing battery max power (W)',
                   'Housing battery average power (W)',
                   'PV max power (W)', 'PV average power',
                   'PV max current (A)', 'PV average current (A)',
                   'Starter battery max voltage (V)', 'Starter battery min voltage (V)',
                   'Starter battery average voltage',
                   'Tank 1 max level', 'Tank 1 min level', 'Tank 1 average level',
                   'Tank 2 max level', 'Tank 2 min level', 'Tank 2 average level']
NMEA_SUMMARY = ['Starting Location (City, Country)',
                'Starting GPS Latitude (d°m\'S\" H)',
                'Starting GPS Longitude (d°m\'S\" H)', 'Ending GPS Latitude (d°m\'S\" H)',
                'Ending GPS Longitude (d°m\'S\" H)', 'Distance (miles)', 'Heading (degrees)',
                'Average Wind Speed (knots)', 'Average Wind Direction (degrees)',
                'Average Water Temperature (°C)', 'Average Depth (meters)',
                'Average Speed Over Ground (knots)', 'Average Speed Over Water (knots)']
VICTRON_METRICS = ['Active Input source', 'Grid 1 power (W)', 'Generator 1 power (W)',
                   'AC Input 1 Voltage (V)', 'AC Input 1 Current (A)', 'AC Input 1 Frequency (Hz)',
                   'VE.Bus State', 'AC Consumption (W)', 'Battery Voltage (V)', 'Battery Current (A)',
                   'Battery Power (W)', 'Battery SOC', 'Battery state', 'PV Power (W)', 'PV Current (A)',
                   'Starter Battery Voltage (V)', 'Tank 1 Level (%)', 'Tank 1 Type', 'Tank 2 Level (%)', 'Tank 2 Type']
NMEA_METRICS = ['True Heading (degrees)', 'True Wind Speed (knots)',
                'True Wind Direction (degrees)', 'Apparent Wind Speed (knots)',
                'Apparent Wind Angle (Relative degrees)', 'GPS Longitude (d°m\'S\" H)',
                'GPS Latitude (d°m\'S\" H)', 'Water Temperature (°C)',
                'Depth (meters)', 'Speed Over Ground (knots)', 'Speed Over Water (knots)',
                'Distance From Previous Entry (miles)', 'Cumulative Distance (miles)']
