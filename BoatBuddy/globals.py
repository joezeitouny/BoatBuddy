from enum import Enum

# General
APPLICATION_NAME = 'Boat Buddy'
APPLICATION_VERSION = '0.14.6'
LOG_FILENAME = 'BoatBuddy.log'
LOG_FILE_SIZE = 1024 * 1024  # Log file size 1MB
LOGGER_NAME = 'BoatBuddy'
INITIAL_SNAPSHOT_INTERVAL = 1  # Time to wait for the first snapshot to be taken after the session starts in seconds
EMPTY_METRIC_VALUE = "N/A"
EARTH_RADIUS = 6371000  # Approximately 6,371 km
JSON_RESPONSE_FORMAT_VERSION = 9

# Anchor manager
ANCHOR_MANAGER_HISTORY_CACHE_LIMIT = 500
ANCHOR_MANAGER_FILENAME = "anchor_alarm.json"
ANCHOR_MANAGER_SAMPLING_RATE = 1  # In seconds
ANCHOR_MANAGER_PERSIST_SESSION_TO_DISK_RATE = 5  # In seconds

# NMEA Plugin
NMEA_PLUGIN_BUFFER_SIZE = 4096
NMEA_PLUGIN_SOCKET_TIMEOUT = 60
NMEA_TIMER_INTERVAL = 1  # In seconds, defines the amount of time to wait between metrics retrievals
NMEA_PLUGIN_SAMPLING_RATE = 0.5  # In seconds

# Victron Modbus TCP Plugin
VICTRON_MODBUS_TCP_TIMER_INTERVAL = 1  # In seconds, defines the amount of time to wait between metrics retrievals
VICTRON_MODBUS_TCP_SAMPLING_RATE = 1  # In seconds

# Victron BLE Plugin
VICTRON_BLE_PLUGIN_SAMPLING_RATE = 1  # In seconds

# GPS Plugin
GPS_TIMER_INTERVAL = 5  # In seconds, defines the amount of time to wait between metrics retrievals
GPS_PLUGIN_SAMPLING_RATE = 0.1  # In seconds


class DataSource(Enum):
    VICTRON_BLE = "victron_ble"
    VICTRON_MODBUS_TCP = "victron_modbus_tcp"


# Session Run modes
class SessionRunMode(Enum):
    AUTO_NMEA = 'auto-nmea'
    AUTO_VICTRON = 'auto-victron'
    AUTO_GPS = 'auto-gps'
    CONTINUOUS = 'continuous'
    INTERVAL = 'interval'
    MANUAL = 'manual'


# Time in seconds between each session is finalized when running in interval mode
SESSION_PAGING_INTERVAL = 60 * 60 * 24  # default is every 24h

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
VICTRON_MODBUS_TCP_PLUGIN_METADATA_HEADERS = ['[GX] Active Input source', '[GX] Grid 1 power (W)',
                                              '[GX] Generator 1 power (W)',
                                              '[GX] AC Input 1 Voltage (V)', '[GX] AC Input 1 Current (A)',
                                              '[GX] AC Input 1 Frequency (Hz)',
                                              '[GX] VE.Bus State', '[GX] AC Consumption (W)', '[GX] Batt. Voltage (V)',
                                              '[GX] Batt. Current (A)',
                                              '[GX] Batt. Power (W)', '[GX] Batt. SOC', '[GX] Batt. state',
                                              '[GX] PV Power (W)',
                                              '[GX] PV Current (A)',
                                              '[GX] Strt. Batt. Voltage (V)', '[GX] Tank 1 lvl (%)', '[GX] Tank 1 Type',
                                              '[GX] Tank 2 lvl (%)',
                                              '[GX] Tank 2 Type']
VICTRON_MODBUS_TCP_PLUGIN_SUMMARY_HEADERS = ['[GX] Batt. max voltage (V)', '[GX] Batt. min voltage (V)',
                                             '[GX] Batt. avg. voltage (V)', '[GX] Batt. max current (A)',
                                             '[GX] Batt. min current (A)', '[GX] Batt. avg. current (A)',
                                             '[GX] Batt. max power (W)', '[GX] Batt. min power (W)',
                                             '[GX] Batt. avg. power (W)',
                                             '[GX] PV max power (W)', '[GX] PV avg. power',
                                             '[GX] PV max current (A)', '[GX] PV avg. current (A)',
                                             '[GX] Strt. batt. max voltage (V)', '[GX] Strt. batt. min voltage (V)',
                                             '[GX] Strt. batt. avg. voltage', '[GX] AC Consumption max (W)',
                                             '[GX] AC Consumption avg. (W)',
                                             '[GX] Tank 1 max lvl', '[GX] Tank 1 min lvl', '[GX] Tank 1 avg. lvl',
                                             '[GX] Tank 2 max lvl', '[GX] Tank 2 min lvl', '[GX] Tank 2 avg. lvl']

VICTRON_BLE_PLUGIN_METADATA_HEADERS = ['[BLE] Housing batt. voltage (V)', '[BLE] Housing batt. current (A)',
                                       '[BLE] Housing batt. power (W)',
                                       '[BLE] Housing batt. SOC', '[BLE] Starter batt. voltage (V)',
                                       '[BLE] Housing batt. consumed Ah', '[BLE] Housing batt. remaining mins',
                                       '[BLE] Auxiliary Temperature (°)']

VICTRON_BLE_PLUGIN_SUMMARY_HEADERS = ['[BLE] Housing batt. max voltage (V)', '[BLE] Housing batt. min voltage (V)',
                                      '[BLE] Housing batt. avg. voltage (V)', '[BLE] Housing batt. max current (A)',
                                      '[BLE] Housing batt. min current (A)', '[BLE] Housing batt. avg. current (A)',
                                      '[BLE] Housing batt. max power (W)', '[BLE] Housing batt. min power (W)',
                                      '[BLE] Housing batt. avg. power (W)',
                                      '[BLE] Housing batt. max SOC',
                                      '[BLE] Housing batt. min SOC', '[BLE] Housing batt. avg. SOC',
                                      '[BLE] Starter batt. max voltage (V)', '[BLE] Starter batt. min voltage (V)',
                                      '[BLE] Starter batt. avg. voltage',
                                      '[BLE] Housing batt. max consumed Ah', '[BLE] Housing batt. min consumed Ah',
                                      '[BLE] Housing batt. avg. consumed Ah',
                                      '[BLE] Housing batt. avg. remaining mins',
                                      '[BLE] Auxiliary Temperature max (°)', '[BLE] Auxiliary Temperature min (°)',
                                      '[BLE] Auxiliary Temperature avg. (°)']
