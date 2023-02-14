# General
APPLICATION_NAME = 'Boat Buddy'
APPLICATION_VERSION = '0.3.0'
LOG_FILENAME = 'BoatBuddy.log'
LOG_FILE_SIZE = 1024 * 1024  # Log file size 1MB
LOGGER_NAME = 'BoatBuddy'
LOG_LEVEL = 'INFO'  # Log level DEBUG, INFO, WARNING, ERROR, CRITICAL
INITIAL_SNAPSHOT_INTERVAL = 1  # Time to wait for the first snapshot to be taken after the session starts in seconds
DEFAULT_DISK_WRITE_INTERVAL = 900  # Entry disk write interval in seconds (15 minutes = 900 seconds)

# NMEA Plugin
DEFAULT_TCP_PORT = 10110
BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 60
NMEA_TIMER_INTERVAL = 1  # In seconds, defines the amount of time to wait between metrics retrievals

# Victron Plugin
MODBUS_TCP_PORT = 502
VICTRON_TIMER_INTERVAL = 1  # In seconds, defines the amount of time to wait between metrics retrievals

# GPS Plugin
GPS_TIMER_INTERVAL = 1  # In seconds, defines the amount of time to wait between metrics retrievals

# Run modes
SESSION_RUN_MODE_AUTO_NMEA = 'auto-nmea'
SESSION_RUN_MODE_AUTO_VICTRON = 'auto-victron'
SESSION_RUN_MODE_AUTO_GPS = 'auto-gps'
SESSION_RUN_MODE_CONTINUOUS = 'continuous'
SESSION_RUN_MODE_INTERVAL = 'interval'
SESSION_RUN_MODE_MANUAL = 'manual'

# Defaults for command line options
DEFAULT_FILENAME_PREFIX = 'Trip_'
DEFAULT_SUMMARY_FILENAME_PREFIX = 'Trip_Summary_'
DEFAULT_CSV_OUTPUT_FLAG = False
DEFAULT_EXCEL_OUTPUT_FLAG = False
DEFAULT_GPX_OUTPUT_FLAG = False
DEFAULT_SUMMARY_OUTPUT_FLAG = False
DEFAULT_VERBOSE_FLAG = False
DEFAULT_SESSION_RUN_MODE = SESSION_RUN_MODE_MANUAL
# Time in seconds between each session is finalized when running in interval mode
DEFAULT_SESSION_INTERVAL = 60 * 60 * 24  # default is every 24h
DEFAULT_NO_SOUND = False
DEFAULT_SHOW_LOG_IN_CONSOLE = False

# Display colouring template
COLOURING_SCHEME = {'Tank 1 lvl (%)': {'green': [80, 100], 'yellow': [60, 80], 'red': [0, 60]},
                    'Tank 2 lvl (%)': {'green': [80, 100], 'yellow': [60, 80], 'red': [0, 60]},
                    'Batt. SOC': {'green': [80, 100], 'yellow': [60, 80], 'red': [0, 60]},
                    'Batt. Voltage (V)': {'green': [12.8, 15], 'yellow': [12.6, 12.8], 'red': [0, 12.6]},
                    'Strt. Batt. Voltage (V)': {'green': [12.8, 15], 'yellow': [12.6, 12.8], 'red': [0, 12.6]},
                    'TWS (kts)': {'green': [0, 18], 'yellow': [18, 25], 'red': [25, 100]},
                    'AWS (kts)': {'green': [0, 18], 'yellow': [18, 25], 'red': [25, 100]},
                    'Depth (m)': {'green': [20, 400], 'yellow': [4, 20], 'red': [0, 4]}}
NOTIFICATIONS_RULES = {'Tank 1 lvl (%)': {'warning': {'range': [60, 80], 'frequency': 'once'},
                                          'alarm': {'range': [0, 60], 'frequency': 'interval',
                                                    'interval': 60 * 60}},  # Every hour
                       'Tank 2 lvl (%)': {'warning': {'range': [60, 80], 'frequency': 'once'},
                                          'alarm': {'range': [0, 60], 'frequency': 'interval',
                                                    'interval': 60 * 60 * 4}},  # Every four hours
                       'Batt. SOC': {'warning': {'range': [60, 80], 'frequency': 'once'},
                                     'alarm': {'range': [0, 60], 'frequency': 'interval', 'interval': 60 * 60}},
                       'Batt. Voltage (V)': {
                           'warning': {'range': [12.6, 12.8], 'frequency': 'once'},
                           'alarm': {'range': [0, 12.6], 'frequency': 'interval', 'interval': 60 * 60}},
                       'Strt. Batt. Voltage (V)': {
                           'warning': {'range': [12.6, 12.8], 'frequency': 'once'},
                           'alarm': {'range': [0, 12.6], 'frequency': 'interval', 'interval': 60 * 60}},
                       'AWS (kts)': {'warning': {'range': [18, 25], 'frequency': 'once'},
                                     'alarm': {'range': [25, 100], 'frequency': 'interval', 'interval': 60 * 15}},
                       'Depth (m)': {'warning': {'range': [4, 20], 'frequency': 'once'},
                                     'alarm': {'range': [0, 4], 'frequency': 'interval', 'interval': 60}}
                       }

# Display filters
FILTERED_SESSION_HEADER = ['Start Time (UTC)', 'Start Time (Local)', 'Duration']
FILTERED_VICTRON_SUMMARY = ['Batt. max voltage (V)', 'Batt. min voltage (V)',
                            'Batt. avg. voltage (V)', 'Batt. max current (A)',
                            'Batt. avg. current (A)', 'Batt. max power (W)',
                            'Batt. avg. power (W)',
                            'PV max power (W)', 'PV avg. power',
                            'PV max current (A)', 'PV avg. current (A)',
                            'Strt. batt. max voltage (V)', 'Strt. batt. min voltage (V)',
                            'Strt. batt. avg. voltage',
                            'Tank 1 max lvl', 'Tank 1 min lvl', 'Tank 1 avg. lvl',
                            'Tank 2 max lvl', 'Tank 2 min lvl', 'Tank 2 avg. lvl']
FILTERED_NMEA_SUMMARY = ['Start Location (City, Country)',
                         'Start GPS Lat (d°m\'S\" H)',
                         'Start GPS Lon (d°m\'S\" H)', 'Dst. (miles)', 'Hdg. (°)',
                         'Avg. Wind Speed (kts)', 'Avg. Wind Direction (°)',
                         'Avg. Water Temp. (°C)', 'Avg. Depth (m)',
                         'Avg. SOG (kts)', 'Avg. SOW (kts)']
FILTERED_VICTRON_METRICS = ['Active Input source', 'Grid 1 power (W)', 'Generator 1 power (W)',
                            'AC Input 1 Voltage (V)', 'AC Input 1 Current (A)', 'AC Input 1 Frequency (Hz)',
                            'VE.Bus State', 'AC Consumption (W)', 'Batt. Voltage (V)', 'Batt. Current (A)',
                            'Batt. Power (W)', 'Batt. SOC', 'Batt. state', 'PV Power (W)', 'PV Current (A)',
                            'Strt. Batt. Voltage (V)', 'Tank 1 lvl (%)', 'Tank 1 Type', 'Tank 2 lvl (%)',
                            'Tank 2 Type']
FILTERED_NMEA_METRICS = ['True Hdg. (°)', 'TWS (kts)',
                         'TWD (°)', 'AWS (kts)',
                         'AWA (Relative °)', 'GPS Lon (d°m\'S\" H)',
                         'GPS Lat (d°m\'S\" H)', 'Water Temp. (°C)',
                         'Depth (m)', 'SOG (kts)', 'SOW (kts)',
                         'Dst. from last entry (miles)', 'Cumulative Dst. (miles)']
FILTERED_GPS_METRICS = ['GPS Lat (d°m\'S\" H)', 'GPS Lon (d°m\'S\" H)', 'Location (City, Country)']

# Default headers (change with caution)
CLOCK_PLUGIN_METADATA_HEADERS = ['UTC Time', 'Local Time']
CLOCK_PLUGIN_SUMMARY_HEADERS = ['Start Time (UTC)', 'Start Time (Local)', 'End Time (UTC)', 'End Time (Local)',
                                'Duration']
GPS_PLUGIN_METADATA_HEADERS = ['GPS Lat (d°m\'S\" H)', 'GPS Lon (d°m\'S\" H)', 'Location (City, Country)']
GPS_PLUGIN_SUMMARY_HEADERS = ['Start Location (City, Country)', 'End Location (City, Country)',
                              'Start GPS Lat (d°m\'S\" H)', 'Start GPS Lon (d°m\'S\" H)', 'End GPS Lat (d°m\'S\" H)',
                              'End GPS Lon (d°m\'S\" H)', 'Dst. (miles)', 'Hdg. (°)']
NMEA_PLUGIN_METADATA_HEADERS = ['True Hdg. (°)', 'TWS (kts)',
                                'TWD (°)', 'AWS (kts)',
                                'AWA (Relative °)', 'GPS Lon (d°m\'S\" H)',
                                'GPS Lat (d°m\'S\" H)', 'Water Temp. (°C)',
                                'Depth (m)', 'SOG (kts)', 'SOW (kts)',
                                'Dst. from last entry (miles)', 'Cumulative Dst. (miles)']
NMEA_PLUGIN_SUMMARY_HEADERS = ['Start Location (City, Country)',
                               'End Location (City, Country)', 'Start GPS Lat (d°m\'S\" H)',
                               'Start GPS Lon (d°m\'S\" H)', 'End GPS Lat (d°m\'S\" H)',
                               'End GPS Lon (d°m\'S\" H)', 'Dst. (miles)', 'Hdg. (°)',
                               'Avg. Wind Speed (kts)', 'Avg. Wind Direction (°)',
                               'Avg. Water Temp. (°C)', 'Avg. Depth (m)',
                               'Avg. SOG (kts)', 'Avg. SOW (kts)']
VICTRON_PLUGIN_METADATA_HEADERS = ['Active Input source', 'Grid 1 power (W)', 'Generator 1 power (W)',
                                   'AC Input 1 Voltage (V)', 'AC Input 1 Current (A)', 'AC Input 1 Frequency (Hz)',
                                   'VE.Bus State', 'AC Consumption (W)', 'Batt. Voltage (V)', 'Batt. Current (A)',
                                   'Batt. Power (W)', 'Batt. SOC', 'Batt. state', 'PV Power (W)',
                                   'PV Current (A)',
                                   'Strt. Batt. Voltage (V)', 'Tank 1 lvl (%)', 'Tank 1 Type', 'Tank 2 lvl (%)',
                                   'Tank 2 Type']
VICTRON_PLUGINS_SUMMARY_HEADERS = ['Batt. max voltage (V)', 'Batt. min voltage (V)',
                                   'Batt. avg. voltage (V)', 'Batt. max current (A)',
                                   'Batt. avg. current (A)', 'Batt. max power (W)',
                                   'Batt. avg. power (W)',
                                   'PV max power (W)', 'PV avg. power',
                                   'PV max current (A)', 'PV avg. current (A)',
                                   'Strt. batt. max voltage (V)', 'Strt. batt. min voltage (V)',
                                   'Strt. batt. avg. voltage', 'AC Consumption max (W)',
                                   'AC Consumption avg. (W)',
                                   'Tank 1 max lvl', 'Tank 1 min lvl', 'Tank 1 avg. lvl',
                                   'Tank 2 max lvl', 'Tank 2 min lvl', 'Tank 2 avg. lvl']
