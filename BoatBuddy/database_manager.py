from enum import Enum
from threading import Thread, Event, Timer
import threading

from BoatBuddy.plugin_manager import PluginManager
from BoatBuddy.notifications_manager import NotificationsManager
from BoatBuddy.mysql_wrapper import MySQLWrapper
from BoatBuddy import utils, globals


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
    def __init__(self, table_name, entry_type: DatabaseEntryType, key_value_list):
        self._table_name = table_name
        self._entry_type = entry_type
        self._key_value_list = key_value_list

    def get_table_name(self):
        return self._table_name

    def get_entry_type(self):
        return self._entry_type

    def get_key_value_list(self):
        return self._key_value_list


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
            self._db_live_feed_timer = Timer(self._options.database_live_feed_interval, self._live_feed_timer_callback)
            self._db_live_feed_timer.start()
            self._db_thread = Thread(target=self._main_loop)
            self._db_thread.start()
            utils.get_logger().info('Database module successfully started!')

    def _live_feed_timer_callback(self):
        if self._exit_signal.is_set():
            return

        # Get a snapshot from the plugin manager instance
        key_value_list = {}
        clock_key_value_list = utils.get_key_value_list(globals.DB_CLOCK_PLUGIN_METADATA_HEADERS,
                                                        self._plugin_manager.get_clock_metrics())
        key_value_list.update(clock_key_value_list)

        if self._options.gps_module:
            gps_plugin_key_value_list = utils.get_key_value_list(globals.DB_GPS_PLUGIN_METADATA_HEADERS,
                                                                 self._plugin_manager.get_gps_plugin_metrics())
            key_value_list.update(gps_plugin_key_value_list)
            gps_plugin_status = self._plugin_manager.get_gps_plugin_status()
            key_value_list.update({'gps_plugin_status': f'{gps_plugin_status}'})

        if self._options.nmea_module:
            nmea_plugin_key_value_list = utils.get_key_value_list(globals.DB_NMEA_PLUGIN_METADATA_HEADERS,
                                                                  self._plugin_manager.get_nmea_plugin_metrics())
            key_value_list.update(nmea_plugin_key_value_list)
            nmea_plugin_status = self._plugin_manager.get_nmea_plugin_status()
            key_value_list.update({'nmea_plugin_status': f'{nmea_plugin_status}'})

        if self._options.victron_module:
            victron_plugin_key_value_list = utils.get_key_value_list(globals.DB_VICTRON_PLUGIN_METADATA_HEADERS,
                                                                     self._plugin_manager.get_victron_plugin_metrics())
            key_value_list.update(victron_plugin_key_value_list)
            victron_plugin_status = self._plugin_manager.get_victron_plugin_status()
            key_value_list.update({'victron_plugin_status': f'{victron_plugin_status}'})

        database_entry = DatabaseEntry('live_feed_entry', DatabaseEntryType.ADD, key_value_list)

        self._mutex.acquire()
        self._db_entries_queue.append(database_entry)
        self._mutex.release()

        # Reset the timer
        self._db_live_feed_timer = Timer(self._options.database_live_feed_interval, self._live_feed_timer_callback)
        self._db_live_feed_timer.start()

    def _main_loop(self):
        while not self._exit_signal.is_set():
            if self._status != DatabaseManagerStatus.RUNNING:
                if self._wrapper.connect_to_server():
                    if not self._wrapper.is_initialised():
                        if self._wrapper.initialise():
                            self._status = DatabaseManagerStatus.RUNNING
            elif len(self._db_entries_queue):
                # Process what is in the queue
                for entry in self._db_entries_queue:
                    self._process_entry(entry)

    def _process_entry(self, database_entry: DatabaseEntry):
        pass

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
