# General
APPLICATION_NAME = 'Boat Buddy'
APPLICATION_VERSION = '0.4.6'
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
DEFAULT_EMAIL_REPORT = False
DEFAULT_NOTIFICATION_COOL_OFF_INTERVAL = 60  # In seconds

# Console colouring rules
COLOURING_SCHEME = {'[GX] Tank 1 lvl (%)': {'green': [80, 100], 'yellow': [60, 80], 'red': [0, 60]},
                    '[GX] Tank 2 lvl (%)': {'green': [80, 100], 'yellow': [60, 80], 'red': [0, 60]},
                    '[GX] Batt. SOC': {'green': [80, 100], 'yellow': [60, 80], 'red': [0, 60]},
                    '[GX] Batt. Voltage (V)': {'green': [12.8, 15], 'yellow': [12.6, 12.8], 'red': [0, 12.6]},
                    '[GX] Strt. Batt. Voltage (V)': {'green': [12.8, 15], 'yellow': [12.6, 12.8], 'red': [0, 12.6]},
                    '[NM] TWS (kts)': {'green': [0, 18], 'yellow': [18, 25], 'red': [25, 100]},
                    '[NM] AWS (kts)': {'green': [0, 18], 'yellow': [18, 25], 'red': [25, 100]},
                    '[NM] Depth (m)': {'green': [20, 400], 'yellow': [4, 20], 'red': [0, 4]}}

# System notification rules
NOTIFICATIONS_RULES = {'[GX] Tank 1 lvl (%)': {'warning': {'range': [60, 80], 'frequency': 'once',
                                                           'notifications': ['sound', 'email'],
                                                           'cool-off-interval': 60 * 5},
                                               'alarm': {'range': [0, 60], 'frequency': 'interval',
                                                         'interval': 60 * 60,  # Every hour
                                                         'notifications': ['sound', 'email'],
                                                         'cool-off-interval': 60 * 5}},
                       '[GX] Tank 2 lvl (%)': {'warning': {'range': [60, 80], 'frequency': 'once',
                                                           'notifications': ['sound', 'email'],
                                                           'cool-off-interval': 60 * 5},
                                               'alarm': {'range': [0, 60], 'frequency': 'interval',
                                                         'interval': 60 * 60 * 4,  # Every four hours
                                                         'notifications': ['sound', 'email'],
                                                         'cool-off-interval': 60 * 5}},
                       '[GX] Batt. SOC': {'warning': {'range': [60, 80], 'frequency': 'once',
                                                      'notifications': ['sound', 'email'],
                                                      'cool-off-interval': 60 * 10},
                                          'alarm': {'range': [0, 60], 'frequency': 'interval', 'interval': 60 * 60,
                                                    'notifications': ['sound', 'email'],
                                                    'cool-off-interval': 60 * 10}},
                       '[GX] Batt. Voltage (V)': {
                           'warning': {'range': [12.6, 12.8], 'frequency': 'once',
                                       'notifications': ['sound', 'email'],
                                       'cool-off-interval': 60 * 10},
                           'alarm': {'range': [0, 12.6], 'frequency': 'interval', 'interval': 60 * 60,
                                     'notifications': ['sound', 'email'],
                                     'cool-off-interval': 60 * 10}},
                       '[GX] Strt. Batt. Voltage (V)': {
                           'warning': {'range': [12.6, 12.8], 'frequency': 'once', 'notifications': ['sound'],
                                       'cool-off-interval': 60 * 10},
                           'alarm': {'range': [0, 12.6], 'frequency': 'interval', 'interval': 60 * 60,
                                     'notifications': ['sound', 'email'], 'cool-off-interval': 60 * 10}},
                       '[NM] AWS (kts)': {
                           'warning': {'range': [18, 25], 'frequency': 'once', 'notifications': ['sound'],
                                       'cool-off-interval': 60 * 15},
                           'alarm': {'range': [25, 100], 'frequency': 'interval', 'interval': 60 * 15,
                                     'notifications': ['sound'],
                                     'cool-off-interval': 60 * 15}},
                       '[NM] Depth (m)': {
                           'warning': {'range': [4, 20], 'frequency': 'once', 'notifications': ['sound']},
                           'alarm': {'range': [0, 4], 'frequency': 'interval', 'interval': 60,
                                     'notifications': ['sound']}}
                       }

# Display filters
FILTERED_SESSION_HEADER = ['Start Time (UTC)', 'Start Time (Local)', 'Duration']
FILTERED_VICTRON_SUMMARY = ['[GX] Batt. max voltage (V)', '[GX] Batt. min voltage (V)',
                            '[GX] Batt. avg. voltage (V)', '[GX] Batt. max current (A)',
                            '[GX] Batt. avg. current (A)', '[GX] Batt. max power (W)',
                            '[GX] Batt. avg. power (W)',
                            '[GX] PV max power (W)', '[GX] PV avg. power',
                            '[GX] PV max current (A)', '[GX] PV avg. current (A)',
                            '[GX] Strt. batt. max voltage (V)', '[GX] Strt. batt. min voltage (V)',
                            '[GX] Strt. batt. avg. voltage',
                            '[GX] Tank 1 max lvl', '[GX] Tank 1 min lvl', '[GX] Tank 1 avg. lvl',
                            '[GX] Tank 2 max lvl', '[GX] Tank 2 min lvl', '[GX] Tank 2 avg. lvl']
FILTERED_NMEA_SUMMARY = ['[NM] Start Location (City, Country)', '[NM] Start GPS Lat (d°m\'S\" H)',
                         '[NM] Start GPS Lon (d°m\'S\" H)', '[NM] Dst. (miles)', '[NM] Hdg. (°)',
                         '[NM] Avg. Wind Speed (kts)', '[NM] Avg. Wind Direction (°)',
                         '[NM] Avg. Water Temp. (°C)', '[NM] Avg. Depth (m)',
                         '[NM] Avg. SOG (kts)', '[NM] Avg. SOW (kts)']
FILTERED_GPS_SUMMARY = ['[SS] Start Location (City, Country)', '[SS] Start GPS Lat (d°m\'S\" H)',
                        '[SS] Start GPS Lon (d°m\'S\" H)',
                        '[SS] Dst. (miles)', '[SS] Hdg. (°)', '[SS] Avg. SOG (kts)']
FILTERED_VICTRON_METRICS = ['[GX] Active Input source', '[GX] Grid 1 power (W)', '[GX] Generator 1 power (W)',
                            '[GX] AC Input 1 Voltage (V)', '[GX] AC Input 1 Current (A)',
                            '[GX] AC Input 1 Frequency (Hz)', '[GX] VE.Bus State', '[GX] AC Consumption (W)',
                            '[GX] Batt. Voltage (V)', '[GX] Batt. Current (A)', '[GX] Batt. Power (W)',
                            '[GX] Batt. SOC', '[GX] Batt. state', '[GX] PV Power (W)',
                            '[GX] PV Current (A)', '[GX] Strt. Batt. Voltage (V)', '[GX] Tank 1 lvl (%)',
                            '[GX] Tank 1 Type', '[GX] Tank 2 lvl (%)', '[GX] Tank 2 Type']
FILTERED_NMEA_METRICS = ['[NM] True Hdg. (°)', '[NM] TWS (kts)',
                         '[NM] TWD (°)', '[NM] AWS (kts)',
                         '[NM] AWA (Relative °)', '[NM] GPS Lat (d°m\'S\" H)',
                         '[NM] GPS Lon (d°m\'S\" H)', '[NM] Water Temp. (°C)',
                         '[NM] Depth (m)', '[NM] SOG (kts)', '[NM] SOW (kts)',
                         '[NM] Dst. from last entry (miles)', '[NM] Cumulative Dst. (miles)']
FILTERED_GPS_METRICS = ['[SS] GPS Lat (d°m\'S\" H)', '[SS] GPS Lon (d°m\'S\" H)', '[SS] Location (City, Country)',
                        '[SS] SOG (kts)', '[SS] COG (°T)', '[SS] Dst. from last entry (miles)',
                        '[SS] Cumulative Dst. (miles)']

# Default headers (change with caution)
CLOCK_PLUGIN_METADATA_HEADERS = ['UTC Time', 'Local Time']
CLOCK_PLUGIN_SUMMARY_HEADERS = ['Start Time (UTC)', 'Start Time (Local)', 'End Time (UTC)', 'End Time (Local)',
                                'Duration']
GPS_PLUGIN_METADATA_HEADERS = ['[SS] GPS Lat (d°m\'S\" H)', '[SS] GPS Lon (d°m\'S\" H)',
                               '[SS] Location (City, Country)', '[SS] SOG (kts)', '[SS] COG (°T)',
                               '[SS] Dst. from last entry (miles)', '[SS] Cumulative Dst. (miles)']
GPS_PLUGIN_SUMMARY_HEADERS = ['[SS] Start Location (City, Country)', '[SS] End Location (City, Country)',
                              '[SS] Start GPS Lat (d°m\'S\" H)', '[SS] Start GPS Lon (d°m\'S\" H)',
                              '[SS] End GPS Lat (d°m\'S\" H)',
                              '[SS] End GPS Lon (d°m\'S\" H)', '[SS] Dst. (miles)', '[SS] Hdg. (°)',
                              '[SS] Avg. SOG (kts)']
NMEA_PLUGIN_METADATA_HEADERS = ['[NM] True Hdg. (°)', '[NM] TWS (kts)',
                                '[NM] TWD (°)', '[NM] AWS (kts)',
                                '[NM] AWA (Relative °)', '[NM] GPS Lat (d°m\'S\" H)',
                                '[NM] GPS Lon (d°m\'S\" H)', '[NM] Water Temp. (°C)',
                                '[NM] Depth (m)', '[NM] SOG (kts)', '[NM] SOW (kts)',
                                '[NM] Dst. from last entry (miles)', '[NM] Cumulative Dst. (miles)']
NMEA_PLUGIN_SUMMARY_HEADERS = ['[NM] Start Location (City, Country)',
                               '[NM] End Location (City, Country)', '[NM] Start GPS Lat (d°m\'S\" H)',
                               '[NM] Start GPS Lon (d°m\'S\" H)', '[NM] End GPS Lat (d°m\'S\" H)',
                               '[NM] End GPS Lon (d°m\'S\" H)', '[NM] Dst. (miles)', '[NM] Hdg. (°)',
                               '[NM] Avg. Wind Speed (kts)', '[NM] Avg. Wind Direction (°)',
                               '[NM] Avg. Water Temp. (°C)', '[NM] Avg. Depth (m)',
                               '[NM] Avg. SOG (kts)', '[NM] Avg. SOW (kts)']
VICTRON_PLUGIN_METADATA_HEADERS = ['[GX] Active Input source', '[GX] Grid 1 power (W)', '[GX] Generator 1 power (W)',
                                   '[GX] AC Input 1 Voltage (V)', '[GX] AC Input 1 Current (A)',
                                   '[GX] AC Input 1 Frequency (Hz)',
                                   '[GX] VE.Bus State', '[GX] AC Consumption (W)', '[GX] Batt. Voltage (V)',
                                   '[GX] Batt. Current (A)',
                                   '[GX] Batt. Power (W)', '[GX] Batt. SOC', '[GX] Batt. state', '[GX] PV Power (W)',
                                   '[GX] PV Current (A)',
                                   '[GX] Strt. Batt. Voltage (V)', '[GX] Tank 1 lvl (%)', '[GX] Tank 1 Type',
                                   '[GX] Tank 2 lvl (%)',
                                   '[GX] Tank 2 Type']
VICTRON_PLUGINS_SUMMARY_HEADERS = ['[GX] Batt. max voltage (V)', '[GX] Batt. min voltage (V)',
                                   '[GX] Batt. avg. voltage (V)', '[GX] Batt. max current (A)',
                                   '[GX] Batt. avg. current (A)', '[GX] Batt. max power (W)',
                                   '[GX] Batt. avg. power (W)',
                                   '[GX] PV max power (W)', '[GX] PV avg. power',
                                   '[GX] PV max current (A)', '[GX] PV avg. current (A)',
                                   '[GX] Strt. batt. max voltage (V)', '[GX] Strt. batt. min voltage (V)',
                                   '[GX] Strt. batt. avg. voltage', '[GX] AC Consumption max (W)',
                                   '[GX] AC Consumption avg. (W)',
                                   '[GX] Tank 1 max lvl', '[GX] Tank 1 min lvl', '[GX] Tank 1 avg. lvl',
                                   '[GX] Tank 2 max lvl', '[GX] Tank 2 min lvl', '[GX] Tank 2 avg. lvl']
