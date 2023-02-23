import threading
from enum import Enum
from threading import Thread, Event, Timer

from BoatBuddy import utils, globals
from BoatBuddy.mysql_wrapper import MySQLWrapper
from BoatBuddy.notifications_manager import NotificationsManager
from BoatBuddy.plugin_manager import PluginManager


class DatabaseManagerStatus(Enum):
    STARTING = 1
    RUNNING = 2
    DOWN = 3


class DatabaseEntryType(Enum):
    ADD = 1
    UPDATE = 2


class DatabaseWrapper(Enum):
    MYSQL = 'mysql'


class DatabaseEntry:
    def __init__(self, table_name, entry_type: DatabaseEntryType, columns, values):
        self._table_name = table_name
        self._entry_type = entry_type
        self._columns = columns
        self._values = values

    def get_table_name(self):
        return self._table_name

    def get_entry_type(self):
        return self._entry_type

    def get_columns(self):
        return self._columns

    def get_values(self):
        return self._values


class DatabaseManager:
    def __init__(self, options, plugin_manager: PluginManager, notifications_manager: NotificationsManager):
        self._options = options
        self._plugin_manager = plugin_manager
        self._notifications_manager = notifications_manager
        self._exit_signal = Event()
        self._status = DatabaseManagerStatus.STARTING
        self._db_entries_queue = []
        self._mutex = threading.Lock()

        if self._options.database_module:
            if self._options.database_wrapper == DatabaseWrapper.MYSQL.value:
                self._wrapper = MySQLWrapper(self._options)
            self._db_live_feed_timer = Timer(self._options.database_live_feed_entry_interval,
                                             self._live_feed_timer_callback)
            self._db_live_feed_timer.start()
            self._db_thread = Thread(target=self._main_loop)
            self._db_thread.start()
            utils.get_logger().info('Database module successfully started!')

    def _live_feed_timer_callback(self):
        if self._exit_signal.is_set():
            return

        # Get a snapshot from the plugin manager instance
        columns = []
        values = []

        # Append the clock metrics
        columns.extend(globals.DB_CLOCK_PLUGIN_METADATA_HEADERS)
        values.extend(self._plugin_manager.get_clock_metrics())

        if self._options.gps_module:
            columns.extend(globals.DB_GPS_PLUGIN_METADATA_HEADERS)
            values.extend(self._plugin_manager.get_gps_plugin_metrics())
            columns.append('gps_plugin_status')
            values.append(self._plugin_manager.get_gps_plugin_status().value)

        if self._options.nmea_module:
            columns.extend(globals.DB_NMEA_PLUGIN_METADATA_HEADERS)
            values.extend(self._plugin_manager.get_nmea_plugin_metrics())
            columns.append('nmea_plugin_status')
            values.append(self._plugin_manager.get_nmea_plugin_status().value)

        if self._options.victron_module:
            columns.extend(globals.DB_VICTRON_PLUGIN_METADATA_HEADERS)
            values.extend(self._plugin_manager.get_victron_plugin_metrics())
            columns.append('victron_plugin_status')
            values.append(self._plugin_manager.get_victron_plugin_status().value)

        database_entry = DatabaseEntry('live_feed_entry', DatabaseEntryType.ADD, columns, values)

        self._mutex.acquire()
        self._db_entries_queue.append(database_entry)
        self._mutex.release()

        # Reset the timer
        self._db_live_feed_timer = Timer(self._options.database_live_feed_entry_interval,
                                         self._live_feed_timer_callback)
        self._db_live_feed_timer.start()

    def _main_loop(self):
        while not self._exit_signal.is_set():
            if self._status != DatabaseManagerStatus.RUNNING:
                if self._wrapper.connect_to_server():
                    if not self._wrapper.is_initialised():
                        if self._wrapper.initialise():
                            self._status = DatabaseManagerStatus.RUNNING
                    else:
                        self._status = DatabaseManagerStatus.RUNNING
            if self._status == DatabaseManagerStatus.RUNNING:
                entries_to_remove = []
                self._mutex.acquire()
                if len(self._db_entries_queue):
                    # Process what is in the queue
                    for entry in self._db_entries_queue:
                        self._process_entry(entry)
                        entries_to_remove.append(entry)

                if len(entries_to_remove) > 0:
                    for entry in entries_to_remove:
                        self._db_entries_queue.remove(entry)
                self._mutex.release()

    def _process_entry(self, database_entry: DatabaseEntry):
        if database_entry.get_entry_type() == DatabaseEntryType.ADD:
            self._wrapper.add_entry(database_entry.get_table_name(), database_entry.get_columns(),
                                    database_entry.get_values())

    def finalize(self):
        if not self._options.database_module:
            return

        self._exit_signal.set()
        if self._db_live_feed_timer:
            self._db_live_feed_timer.cancel()
        if self._db_thread:
            self._db_thread.join()

        self._status = DatabaseManagerStatus.DOWN
        utils.get_logger().info('Database manager instance is ready to be destroyed')
