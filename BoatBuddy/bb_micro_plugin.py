import threading
from events import Events
import requests

from BoatBuddy import globals, utils
from BoatBuddy.generic_plugin import GenericPlugin, PluginStatus


class BBMicroPluginEvents(Events):
    __events__ = ('on_connect', 'on_disconnect',)


class BBMicroEntry:
    def __init__(self, air_temperature, humidity, air_quality, barometric_pressure, relay_1, relay_2, relay_3,
                 relay_4, relay_5, relay_6):
        self._air_temperature = air_temperature
        self._humidity = humidity
        self._air_quality = air_quality
        self._barometric_pressure = barometric_pressure
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
                f'{self._barometric_pressure}',
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
        self._relay_1 = False
        self._relay_2 = False
        self._relay_3 = False
        self._relay_4 = False
        self._relay_5 = False
        self._relay_6 = False

        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]
        self._sum_air_temperature = 0
        self._cnt_air_temperature_entries = 0
        self._sum_humidity = 0
        self._cnt_humidity_entries = 0
        self._sum_air_quality = 0
        self._cnt_air_quality_entries = 0
        self._sum_barometric_pressure = 0
        self._cnt_barometric_pressure_entries = 0

        # Other instance variables
        self._plugin_status = PluginStatus.STARTING
        self._exit_signal = threading.Event()
        self._timer = threading.Timer(globals.BB_MICRO_TIMER_INTERVAL, self._main_loop)
        self._timer.start()
        self._log_manager.info('BB Micro plugin successfully started!')

    def _reset_instance_metrics(self):
        # Instance metrics
        self._air_temperature = globals.EMPTY_METRIC_VALUE
        self._humidity = globals.EMPTY_METRIC_VALUE
        self._air_quality = globals.EMPTY_METRIC_VALUE
        self._barometric_pressure = globals.EMPTY_METRIC_VALUE
        self._relay_1 = False
        self._relay_2 = False
        self._relay_3 = False
        self._relay_4 = False
        self._relay_5 = False
        self._relay_6 = False

        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]
        self._sum_air_temperature = 0
        self._cnt_air_temperature_entries = 0
        self._sum_humidity = 0
        self._cnt_humidity_entries = 0
        self._sum_air_quality = 0
        self._cnt_air_quality_entries = 0
        self._sum_barometric_pressure = 0
        self._cnt_barometric_pressure_entries = 0

    def _main_loop(self):
        if self._exit_signal.is_set():
            self._plugin_status = PluginStatus.DOWN
            self._log_manager.info('BB Micro plugin instance is ready to be destroyed')
            return

        # Query the metrics from the BB Micro module
        bb_micro_ip_address = self._options.bb_micro_ip

        # URL of the API endpoint
        base_url = f"http://{bb_micro_ip_address}"
        version_url = f"{base_url}/text_sensor/project_version"
        sensors_url = f"{base_url}/sensor"
        air_quality_url = f"{sensors_url}/mq2_smoke_sensor"
        humidity_url = f"{sensors_url}/room_humidity"
        air_temperature_url = f"{sensors_url}/room_temperature"
        barometric_pressure_url = f"{sensors_url}/atmospheric_pressure"
        relays_url = f"{base_url}/switch/switch_"

        try:
            # Make a GET request to the metrics API
            response = requests.get(version_url, timeout=globals.BB_MICRO_REQUESTS_TIMEOUT)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                if self._plugin_status != PluginStatus.RUNNING:
                    self._log_manager.info(f'Connection to BB Micro device on {bb_micro_ip_address} is established')

                    self._plugin_status = PluginStatus.RUNNING

                    self._reset_instance_metrics()

                    if self._events:
                        self._events.on_connect()

                # get air quality metric
                response = requests.get(air_quality_url, timeout=globals.BB_MICRO_REQUESTS_TIMEOUT)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Parse the JSON response
                    data = response.json()

                    self._air_quality = data["value"]

                # get air temperature metric
                response = requests.get(air_temperature_url, timeout=globals.BB_MICRO_REQUESTS_TIMEOUT)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Parse the JSON response
                    data = response.json()

                    self._air_temperature = data["value"]

                # get humidity metric
                response = requests.get(humidity_url, timeout=globals.BB_MICRO_REQUESTS_TIMEOUT)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Parse the JSON response
                    data = response.json()

                    self._humidity = data["value"]

                # get barometric pressure metric
                response = requests.get(barometric_pressure_url, timeout=globals.BB_MICRO_REQUESTS_TIMEOUT)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Parse the JSON response
                    data = response.json()

                    self._barometric_pressure = data["value"]

                for i in range(1, 7):
                    # get relay value
                    response = requests.get(f"{relays_url}{i}", timeout=globals.BB_MICRO_REQUESTS_TIMEOUT)

                    # Check if the request was successful (status code 200)
                    if response.status_code == 200:
                        # Parse the JSON response
                        data = response.json()

                        value = utils.try_parse_bool(data["value"])
                        if i == 1:
                            self._relay_1 = value
                        elif i == 2:
                            self._relay_2 = value
                        elif i == 3:
                            self._relay_3 = value
                        elif i == 4:
                            self._relay_4 = value
                        elif i == 5:
                            self._relay_5 = value
                        elif i == 6:
                            self._relay_6 = value
        except Exception as e:
            self._handle_connection_exception(e)

        # Reset the timer
        self._timer = threading.Timer(globals.BB_MICRO_TIMER_INTERVAL, self._main_loop)
        self._timer.start()

    def _handle_connection_exception(self, message):
        if self._plugin_status != PluginStatus.DOWN:
            self._log_manager.info(
                f'Problem with BB Micro system on {self._options.victron_modbus_tcp_server_ip}. Details: {message}')

            self._plugin_status = PluginStatus.DOWN

            # If anyone is listening to events then notify of a disconnection
            if self._events:
                self._events.on_disconnect()

    def get_metadata_headers(self):
        return globals.BB_MICRO_PLUGIN_METADATA_HEADERS.copy()

    def take_snapshot(self, store_entry):
        entry = BBMicroEntry(self._air_temperature, self._humidity, self._air_quality,
                             self._barometric_pressure,
                             self._relay_1, self._relay_2, self._relay_3,
                             self._relay_4, self._relay_5, self._relay_6)

        if store_entry:
            self._log_manager.debug(f'Adding new BB Micro entry')
            self._log_manager.debug(f'Air temperature: {self._air_temperature} °C' +
                                    f'Humidity: {self._humidity} %' +
                                    f'Air Quality: {self._air_quality} ppm' +
                                    f'Barometric Pressure: {self._barometric_pressure} hPa' +
                                    f'Relay 1: {self._relay_1}' +
                                    f'Relay 2: {self._relay_2}' +
                                    f'Relay 3: {self._relay_3}' +
                                    f'Relay 4: {self._relay_4}' +
                                    f'Relay 5: {self._relay_5}' +
                                    f'Relay 6: {self._relay_6}')

            self._log_entries.append(entry)

            # Calculate extremes and averages
            if entry.air_temperature != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[0] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[0] = entry.air_temperature
                else:
                    self._summary_values[0] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.air_temperature),
                                                 self._summary_values[0])

                if self._summary_values[1] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[1] = entry.air_temperature
                else:
                    self._summary_values[1] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.air_temperature),
                                                  self._summary_values[1])

                self._sum_air_temperature += utils.try_parse_float(entry.air_temperature)
                self._cnt_air_temperature_entries += 1
                if self._summary_values[2] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[2] = entry.air_temperature
                else:
                    self._summary_values[2] = \
                        round(self._sum_air_temperature / self._cnt_air_temperature_entries, 1)

            if entry.humidity != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[3] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[3] = entry.humidity
                else:
                    self._summary_values[3] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.humidity),
                                                 self._summary_values[3])

                if self._summary_values[4] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[4] = entry.humidity
                else:
                    self._summary_values[4] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.humidity),
                                                  self._summary_values[4])

                self._sum_humidity += utils.try_parse_int(entry.humidity)
                self._cnt_humidity_entries += 1
                if self._summary_values[5] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[5] = entry.humidity
                else:
                    self._summary_values[5] = \
                        round(self._sum_humidity / self._cnt_humidity_entries, 0)

            if entry.air_quality != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[6] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[6] = entry.air_quality
                else:
                    self._summary_values[6] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.air_quality),
                                                 self._summary_values[6])

                if self._summary_values[7] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[7] = entry.air_quality
                else:
                    self._summary_values[7] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.air_quality),
                                                  self._summary_values[7])

                self._sum_air_quality += utils.try_parse_int(entry.air_quality)
                self._cnt_air_quality_entries += 1
                if self._summary_values[8] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[8] = entry.air_quality
                else:
                    self._summary_values[8] = \
                        round(self._sum_air_quality / self._cnt_air_quality_entries, 0)

            if entry.barometric_pressure != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[9] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[9] = entry.barometric_pressure
                else:
                    self._summary_values[9] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.barometric_pressure),
                                                 self._summary_values[9])

                if self._summary_values[10] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[10] = entry.barometric_pressure
                else:
                    self._summary_values[10] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.barometric_pressure),
                                                  self._summary_values[10])

                self._sum_barometric_pressure += utils.try_parse_int(entry.barometric_pressure)
                self._cnt_barometric_pressure_entries += 1
                if self._summary_values[11] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[11] = entry.barometric_pressure
                else:
                    self._summary_values[11] = \
                        round(self._sum_barometric_pressure / self._cnt_barometric_pressure_entries, 0)

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

        bb_micro_ip_address = self._options.bb_micro_ip

        # URL of the API endpoint
        base_url = f"http://{bb_micro_ip_address}"
        toggle_relay_url = f"{base_url}/switch/switch_{relay_number}/toggle"

        try:
            # Make a GET request to the metrics API
            response = requests.get(toggle_relay_url)

            # Check if the request was successful (status code 200)
            return response.status_code == 200
        except Exception as e:
            self._log_manager.info(f'Could not toggle relay with relay number: {relay_number}. Details {e}')
            return False
