import threading
from events import Events

from BoatBuddy import globals, utils
from BoatBuddy.generic_plugin import GenericPlugin, PluginStatus


class BBMicroPluginEvents(Events):
    __events__ = ('on_connect', 'on_disconnect',)


class BBMicroEntry:
    def __init__(self, air_temperature, humidity, air_quality, barometric_pressure, altitude, relay_1, relay_2, relay_3,
                 relay_4, relay_5, relay_6):
        self._air_temperature = air_temperature
        self._humidity = humidity
        self._air_quality = air_quality
        self._barometric_pressure = barometric_pressure
        self._altitude = altitude
        self._relay_1 = relay_1
        self._relay_2 = relay_2
        self._relay_3 = relay_3
        self._relay_4 = relay_4
        self._relay_5 = relay_5
        self._relay_6 = relay_6

    def __str__(self):
        return utils.get_comma_separated_string(self.get_values())

    def get_values(self):
        return [f'{self._air_temperature}', f'{self._humidity}', f'{self._air_quality}',
                f'{self._barometric_pressure}', f'{self._altitude}',
                f'{self._relay_1}', f'{self._relay_2}', f'{self._relay_3}',
                f'{self._relay_4}', f'{self._relay_5}', f'{self._relay_6}']

    @property
    def air_temperature(self):
        return self._air_temperature

    @property
    def humidity(self):
        return self._humidity

    @property
    def air_quality(self):
        return self._air_quality

    @property
    def barometric_pressure(self):
        return self._barometric_pressure

    @property
    def altitude(self):
        return self._altitude

    @property
    def relay_1(self):
        return self._relay_1

    @property
    def relay_2(self):
        return self._relay_2

    @property
    def relay_3(self):
        return self._relay_3

    @property
    def relay_4(self):
        return self._relay_4

    @property
    def relay_5(self):
        return self._relay_5

    @property
    def relay_6(self):
        return self._relay_6


class BBMicroPlugin(GenericPlugin):

    def __init__(self, options, log_manager):
        # invoking the __init__ of the parent class
        GenericPlugin.__init__(self, options, log_manager)

        self._events = None

        # Instance metrics
        self._air_temperature = globals.EMPTY_METRIC_VALUE
        self._humidity = globals.EMPTY_METRIC_VALUE
        self._air_quality = globals.EMPTY_METRIC_VALUE
        self._barometric_pressure = globals.EMPTY_METRIC_VALUE
        self._altitude = globals.EMPTY_METRIC_VALUE
        self._relay_1 = False
        self._relay_2 = False
        self._relay_3 = False
        self._relay_4 = False
        self._relay_5 = False
        self._relay_6 = False

        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                False, False, False, False, False, False]

        # Other instance variables
        self._plugin_status = PluginStatus.STARTING
        self._exit_signal = threading.Event()
        self._timer = threading.Timer(globals.VICTRON_MODBUS_TCP_TIMER_INTERVAL, self._main_loop)
        self._timer.start()
        self._log_manager.info('BB Micro plugin successfully started!')

    def _main_loop(self):
        if self._exit_signal.is_set():
            self._plugin_status = PluginStatus.DOWN
            self._log_manager.info('BB Micro plugin instance is ready to be destroyed')
            return

        # TODO: Query the metrics from the BB Micro module
        bb_micro_ip_address = self._options.bb_micro_server_ip
        bb_micro_port = self._options.bb_micro_server_port


        # Reset the timer
        self._timer = threading.Timer(globals.VICTRON_MODBUS_TCP_TIMER_INTERVAL, self._main_loop)
        self._timer.start()

    def _handle_connection_exception(self, message):
        if self._plugin_status != PluginStatus.DOWN:
            self._log_manager.info(
                f'Problem with Victron Modbus TCP system on {self._options.victron_modbus_tcp_server_ip}. Details: {message}')

            self._plugin_status = PluginStatus.DOWN

            # If anyone is listening to events then notify of a disconnection
            if self._events:
                self._events.on_disconnect()

    def get_metadata_headers(self):
        return globals.VICTRON_MODBUS_TCP_PLUGIN_METADATA_HEADERS.copy()

    def take_snapshot(self, store_entry):
        entry = BBMicroEntry(self._air_temperature, self._humidity, self._air_quality,
                             self._barometric_pressure, self._altitude,
                             self._relay_1, self._relay_2, self._relay_3,
                             self._relay_4, self._relay_5, self._relay_6)

        if store_entry:
            self._log_manager.debug(f'Adding new BB Micro entry')
            self._log_manager.debug(f'Air temperature: {self._air_temperature} °C' +
                                    f'Humidity: {self._humidity} %' +
                                    f'Air Quality: {self._air_quality} ppm' +
                                    f'Barometric Pressure: {self._barometric_pressure} hPa' +
                                    f'Altitude: {self._altitude} m' +
                                    f'Relay 1: {self._relay_1}' +
                                    f'Relay 2: {self._relay_2}' +
                                    f'Relay 3: {self._relay_3}' +
                                    f'Relay 4: {self._relay_4}' +
                                    f'Relay 5: {self._relay_5}' +
                                    f'Relay 6: {self._relay_6}')

            self._log_entries.append(entry)

        return entry

    def get_metadata_values(self):
        if len(self._log_entries) > 0:
            return self._log_entries[len(self._log_entries) - 1].get_values()
        else:
            return []

    def finalize(self):
        self._exit_signal.set()
        if self._timer:
            self._timer.cancel()
        self._log_manager.info("BB Micro plugin worker thread notified...")

    def get_summary_headers(self):
        return globals.BB_MICRO_PLUGIN_SUMMARY_HEADERS.copy()

    def get_summary_values(self):
        return self._summary_values.copy()

    def get_status(self) -> PluginStatus:
        return self._plugin_status

    def register_for_events(self, events):
        self._events = events

    def toggle_relay(self, relay_number):
        if self._exit_signal.is_set():
            return False

        #TODO: Toggle the relay with the specified number
