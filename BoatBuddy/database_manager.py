import threading
import time
from enum import Enum
from threading import Thread, Event, Timer

from BoatBuddy import globals
from BoatBuddy.log_manager import LogManager, LogEvents, LogType
from BoatBuddy.mysql_wrapper import MySQLWrapper
from BoatBuddy.notifications_manager import NotificationsManager, NotificationEvents, NotificationEntryType
from BoatBuddy.plugin_manager import PluginManager, PluginManagerEvents


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
    def __init__(self, options, log_manager: LogManager, plugin_manager: PluginManager,
                 notifications_manager: NotificationsManager):
        self._options = options
        self._log_manager = log_manager
        self._plugin_manager = plugin_manager
        self._notifications_manager = notifications_manager
        self._exit_signal = Event()
        self._status = DatabaseManagerStatus.STARTING
        self._db_entries_queue = []
        self._mutex = threading.Lock()

        if self._options.database_module:
            log_events = LogEvents()
            log_events.on_log += self._on_log
            self._log_manager.register_for_events(log_events)

            notifications_events = NotificationEvents()
            notifications_events.on_notification += self._on_notification
            self._notifications_manager.register_for_events(notifications_events)

            plugin_manager_events = PluginManagerEvents()
            plugin_manager_events.on_snapshot += self._on_plugin_manager_snapshot
            plugin_manager_events.on_session_report += self._on_plugin_manager_session_report
            self._plugin_manager.register_for_events(plugin_manager_events)

            if self._options.database_wrapper == DatabaseWrapper.MYSQL.value:
                self._wrapper = MySQLWrapper(self._options, self._log_manager)
            self._db_live_feed_timer = Timer(self._options.database_live_feed_entry_interval,
                                             self._live_feed_timer_callback)
            self._db_live_feed_timer.start()
            self._db_thread = Thread(target=self._main_loop)
            self._db_thread.start()
            self._log_manager.info('Database module successfully started!')

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

    def _on_log(self, log_type: LogType, message):
        columns = ['type', 'message']
        values = [log_type.value, message]
        database_entry = DatabaseEntry('log', DatabaseEntryType.ADD, columns, values)

        self._mutex.acquire()
        self._db_entries_queue.append(database_entry)
        self._mutex.release()

    def _on_notification(self, notification_entry_type: NotificationEntryType, message):
        columns = ['type', 'message']
        values = [notification_entry_type.value, message]
        database_entry = DatabaseEntry('event', DatabaseEntryType.ADD, columns, values)

        self._mutex.acquire()
        self._db_entries_queue.append(database_entry)
        self._mutex.release()

    def _on_plugin_manager_snapshot(self, session_id, values):
        columns = []
        # Append the clock metrics
        columns.extend(globals.DB_CLOCK_PLUGIN_METADATA_HEADERS)

        if self._options.gps_module:
            columns.extend(globals.DB_GPS_PLUGIN_METADATA_HEADERS)

        if self._options.nmea_module:
            columns.extend(globals.DB_NMEA_PLUGIN_METADATA_HEADERS)

        if self._options.victron_module:
            columns.extend(globals.DB_VICTRON_PLUGIN_METADATA_HEADERS)

        columns.append('session_id')
        values.append(session_id)

        database_entry = DatabaseEntry('session_entry', DatabaseEntryType.ADD, columns, values)

        self._mutex.acquire()
        self._db_entries_queue.append(database_entry)
        self._mutex.release()

    def _on_plugin_manager_session_report(self, session_id, values):
        columns = []
        # Append the clock metrics
        columns.extend(globals.DB_CLOCK_PLUGIN_SUMMARY_HEADERS)

        if self._options.gps_module:
            columns.extend(globals.DB_GPS_PLUGIN_SUMMARY_HEADERS)

        if self._options.nmea_module:
            columns.extend(globals.DB_NMEA_PLUGIN_SUMMARY_HEADERS)

        if self._options.victron_module:
            columns.extend(globals.DB_VICTRON_PLUGINS_SUMMARY_HEADERS)

        columns.append('session_id')
        values.append(session_id)

        database_entry = DatabaseEntry('session', DatabaseEntryType.ADD, columns, values)

        self._mutex.acquire()
        self._db_entries_queue.append(database_entry)
        self._mutex.release()

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
                try:
                    if len(self._db_entries_queue):
                        # Process what is in the queue
                        for entry in self._db_entries_queue:
                            self._process_entry(entry)
                            entries_to_remove.append(entry)

                    if len(entries_to_remove) > 0:
                        for entry in entries_to_remove:
                            self._db_entries_queue.remove(entry)
                except Exception as e:
                    self._handle_exception(e)
                self._mutex.release()
            time.sleep(1)

    def _process_entry(self, database_entry: DatabaseEntry):
        if database_entry.get_entry_type() == DatabaseEntryType.ADD:
            self._wrapper.add_entry(database_entry.get_table_name(), database_entry.get_columns(),
                                    database_entry.get_values())

    def _handle_exception(self, message):
        if self._status != DatabaseManagerStatus.DOWN:
            self._log_manager.info(f'Problem with the Database module. Details: {message}')

            self._status = DatabaseManagerStatus.DOWN

    def finalize(self):
        if not self._options.database_module:
            return

        self._exit_signal.set()
        if self._db_live_feed_timer:
            self._db_live_feed_timer.cancel()
        if self._db_thread:
            self._db_thread.join()

        self._status = DatabaseManagerStatus.DOWN
        self._log_manager.info('Database manager instance is ready to be destroyed')
