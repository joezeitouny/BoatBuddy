import asyncio
import threading

from bleak import BleakScanner

from victron_ble.devices import detect_device_type
from victron_ble.exceptions import UnknownDeviceError

from BoatBuddy import globals, utils
from BoatBuddy.generic_plugin import GenericPlugin, PluginStatus


class VictronBLEBMVDeviceEntry:
    def __init__(self, housing_battery_soc, housing_battery_voltage, housing_battery_current,
                 starter_battery_voltage, housing_battery_consumed_ah, housing_battery_remaining_mins):
        self._housing_battery_soc = housing_battery_soc
        self._housing_battery_voltage = housing_battery_voltage
        self._housing_battery_current = housing_battery_current
        self._starter_battery_voltage = starter_battery_voltage
        self._housing_battery_consumed_ah = housing_battery_consumed_ah
        self._housing_battery_remaining_mins = housing_battery_remaining_mins

    def __str__(self):
        return utils.get_comma_separated_string(self.get_values())

    def get_values(self):
        return [f'{self._housing_battery_voltage}', f'{self._housing_battery_current}',
                f'{self._housing_battery_soc}', f'{self._starter_battery_voltage}',
                f'{self._housing_battery_consumed_ah}',
                f'{self._housing_battery_remaining_mins}']

    @property
    def housing_battery_soc(self):
        return self._housing_battery_soc

    @property
    def housing_battery_voltage(self):
        return self._housing_battery_voltage

    @property
    def housing_battery_current(self):
        return self._housing_battery_current

    @property
    def starter_battery_voltage(self):
        return self._starter_battery_voltage

    @property
    def housing_battery_consumed_ah(self):
        return self._housing_battery_consumed_ah

    @property
    def housing_battery_remaining_mins(self):
        return self._housing_battery_remaining_mins


class VictronBLEPlugin(GenericPlugin):
    def __init__(self, options, log_manager):
        # invoking the __init__ of the parent class
        GenericPlugin.__init__(self, options, log_manager)

        # Instance metrics
        self._housing_battery_soc = globals.EMPTY_METRIC_VALUE
        self._housing_battery_voltage = globals.EMPTY_METRIC_VALUE
        self._housing_battery_current = globals.EMPTY_METRIC_VALUE
        self._starter_battery_voltage = globals.EMPTY_METRIC_VALUE
        self._housing_battery_consumed_ah = globals.EMPTY_METRIC_VALUE
        self._housing_battery_remaining_mins = globals.EMPTY_METRIC_VALUE

        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]

        self._sum_housing_battery_voltage = 0
        self._cnt_housing_battery_voltage_entries = 0
        self._sum_housing_battery_current = 0
        self._cnt_housing_battery_current_entries = 0
        self._sum_housing_battery_soc = 0
        self._cnt_housing_battery_soc_entries = 0
        self._sum_starter_battery_voltage = 0
        self._cnt_starter_battery_voltage_entries = 0
        self._sum_housing_battery_consumed_ah = 0
        self._cnt_housing_battery_consumed_ah_entries = 0
        self._sum_housing_battery_remaining_mins = 0
        self._cnt_housing_battery_remaining_mins_entries = 0

        self._bmv_device_address = self._options.victron_ble_bmv_device_address
        self._bmv_device_advertisement_key = self._options.victron_ble_bmv_device_advertisement_key

        # Other instance variables
        self._plugin_status = PluginStatus.STARTING
        self._exit_signal = threading.Event()
        # Create and start a separate thread for scanning for ble devices
        scan_thread = threading.Thread(target=self._scan_ble_thread)
        scan_thread.start()
        self._log_manager.info('Victron BLE module successfully started!')

    def _reset_instance_metrics(self):
        self._housing_battery_soc = globals.EMPTY_METRIC_VALUE
        self._housing_battery_voltage = globals.EMPTY_METRIC_VALUE
        self._housing_battery_current = globals.EMPTY_METRIC_VALUE
        self._starter_battery_voltage = globals.EMPTY_METRIC_VALUE
        self._housing_battery_consumed_ah = globals.EMPTY_METRIC_VALUE
        self._housing_battery_remaining_mins = globals.EMPTY_METRIC_VALUE

        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]

        self._sum_housing_battery_voltage = 0
        self._cnt_housing_battery_voltage_entries = 0
        self._sum_housing_battery_current = 0
        self._cnt_housing_battery_current_entries = 0
        self._sum_housing_battery_soc = 0
        self._cnt_housing_battery_soc_entries = 0
        self._sum_starter_battery_voltage = 0
        self._cnt_starter_battery_voltage_entries = 0
        self._sum_housing_battery_consumed_ah = 0
        self._cnt_housing_battery_consumed_ah_entries = 0
        self._sum_housing_battery_remaining_mins = 0
        self._cnt_housing_battery_remaining_mins_entries = 0

    async def _main_loop(self):
        # Function to run the scanning process
        while not self._exit_signal.is_set():
            try:
                scanner = BleakScanner(detection_callback=self._on_detection)
                await scanner.start()

                if self._plugin_status != PluginStatus.RUNNING:
                    self._log_manager.info(f'Victron BLE plugin is actively scanning for BLE devices')

                    self._plugin_status = PluginStatus.RUNNING

                await asyncio.sleep(10)  # Scan for 10 seconds
                await scanner.stop()
            except Exception as e:
                self._handle_connection_exception(e)

        self._plugin_status = PluginStatus.DOWN
        self._log_manager.info('Victron BLE plugin instance is ready to be destroyed')

    def _on_detection(self, device, advertisement_data):
        # Callback function to handle device detection
        try:
            if not device.address == self._bmv_device_address:
                return

            raw_data = advertisement_data.manufacturer_data.get(0x02E1)
            if not raw_data or not raw_data.startswith(b"\x10"):
                return
            else:
                device_klass = detect_device_type(raw_data)
                if not device_klass:
                    raise UnknownDeviceError(f"Could not identify device type for {device.address}")
                ble_device = device_klass(self._bmv_device_advertisement_key)
                parsed_data = ble_device.parse(raw_data)

                self._housing_battery_voltage = round(parsed_data.get_voltage(), 2)
                self._housing_battery_current = round(parsed_data.get_current(), 1)
                self._housing_battery_soc = round(parsed_data.get_soc())
                self._starter_battery_voltage = round(parsed_data.get_starter_voltage(), 2)
                self._housing_battery_consumed_ah = round(parsed_data.get_consumed_ah(), 1)
                self._housing_battery_remaining_mins = parsed_data.get_remaining_mins()
        except Exception as e:
            self._handle_connection_exception(e)

    def _scan_ble_thread(self):
        # Function to run the scanning process in a separate thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._main_loop())

    def finalize(self):
        self._exit_signal.set()
        self._log_manager.info("Victron BLE plugin worker thread notified...")

    def _handle_connection_exception(self, message):
        if self._plugin_status != PluginStatus.DOWN:
            self._log_manager.info(
                f'Problem with Victron BLE plugin. Details: {message}')

            self._plugin_status = PluginStatus.DOWN

    def get_status(self) -> PluginStatus:
        return self._plugin_status

    def get_metadata_headers(self):
        return globals.VICTRON_BLE_PLUGIN_METADATA_HEADERS.copy()

    # Collect all current data in an object in memory (add that object to a list instance if needed)
    def take_snapshot(self, store_entry):
        entry = VictronBLEBMVDeviceEntry(housing_battery_soc=self._housing_battery_soc,
                                         housing_battery_voltage=self._housing_battery_voltage,
                                         housing_battery_current=self._housing_battery_current,
                                         starter_battery_voltage=self._starter_battery_voltage,
                                         housing_battery_consumed_ah=self._housing_battery_consumed_ah,
                                         housing_battery_remaining_mins=self._housing_battery_remaining_mins)
        if store_entry:
            self._log_manager.debug(f'Adding new Victron BLE entry')
            self._log_manager.debug(f'Housing Battery SOC: {entry.housing_battery_soc} ' +
                                    f'Housing Battery Voltage: {entry.housing_battery_voltage} V ' +
                                    f'Housing Battery Current: {entry.housing_battery_current} A ' +
                                    f'Starter Battery Voltage: {entry.starter_battery_voltage} V' +
                                    f'Housing Battery Consumed Ah: {entry.housing_battery_consumed_ah}' +
                                    f'Housing Battery Remaining mins: {entry.housing_battery_remaining_mins}')

            self._log_entries.append(entry)

            # Calculate extremes and averages
            if entry.housing_battery_voltage != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[0] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[0] = entry.housing_battery_voltage
                else:
                    self._summary_values[0] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.housing_battery_voltage),
                                                 self._summary_values[0])

                if self._summary_values[1] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[1] = entry.housing_battery_voltage
                else:
                    self._summary_values[1] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.housing_battery_voltage),
                                                  self._summary_values[1])

                self._sum_housing_battery_voltage += utils.try_parse_float(entry.housing_battery_voltage)
                self._cnt_housing_battery_voltage_entries += 1
                if self._summary_values[2] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[2] = entry.housing_battery_voltage
                else:
                    self._summary_values[2] = \
                        round(self._sum_housing_battery_voltage / self._cnt_housing_battery_voltage_entries, 2)

            if entry.housing_battery_current != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[3] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[3] = entry.housing_battery_current
                else:
                    self._summary_values[3] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.housing_battery_current),
                                                 self._summary_values[3])

                self._sum_housing_battery_current += utils.try_parse_float(entry.housing_battery_current)
                self._cnt_housing_battery_current_entries += 1
                if self._summary_values[4] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[4] = entry.housing_battery_current
                else:
                    self._summary_values[4] = \
                        round(self._sum_housing_battery_current / self._cnt_housing_battery_current_entries, 2)

            if entry.housing_battery_soc != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[5] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[5] = entry.housing_battery_soc
                else:
                    self._summary_values[5] = \
                        utils.get_biggest_number(utils.try_parse_int(entry.housing_battery_soc),
                                                 self._summary_values[5])

                if self._summary_values[6] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[6] = entry.housing_battery_soc
                else:
                    self._summary_values[6] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.housing_battery_soc),
                                                  self._summary_values[6])

                self._sum_housing_battery_soc += utils.try_parse_int(entry.housing_battery_soc)
                self._cnt_housing_battery_soc_entries += 1
                if self._summary_values[7] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[7] = entry.housing_battery_soc
                else:
                    self._summary_values[7] = \
                        round(self._sum_housing_battery_soc / self._cnt_housing_battery_soc_entries)

            if entry.starter_battery_voltage != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[8] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[8] = entry.starter_battery_voltage
                else:
                    self._summary_values[8] = \
                        utils.get_biggest_number(utils.try_parse_int(entry.starter_battery_voltage),
                                                 self._summary_values[8])

                if self._summary_values[9] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[9] = entry.starter_battery_voltage
                else:
                    self._summary_values[9] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.starter_battery_voltage),
                                                  self._summary_values[9])

                self._sum_starter_battery_voltage += utils.try_parse_int(entry.starter_battery_voltage)
                self._cnt_starter_battery_voltage_entries += 1
                if self._summary_values[10] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[10] = entry.starter_battery_voltage
                else:
                    self._summary_values[10] = round(
                        self._sum_starter_battery_voltage / self._cnt_starter_battery_voltage_entries)

            if entry.housing_battery_consumed_ah != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[11] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[11] = entry.housing_battery_consumed_ah
                else:
                    self._summary_values[11] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.housing_battery_consumed_ah),
                                                 self._summary_values[11])

                if self._summary_values[12] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[12] = entry.housing_battery_consumed_ah
                else:
                    self._summary_values[12] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.housing_battery_consumed_ah),
                                                  self._summary_values[12])

                self._sum_housing_battery_consumed_ah += utils.try_parse_float(entry.housing_battery_consumed_ah)
                self._cnt_housing_battery_consumed_ah_entries += 1
                if self._summary_values[13] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[13] = entry.housing_battery_consumed_ah
                else:
                    self._summary_values[13] = \
                        round(self._sum_housing_battery_consumed_ah / self._cnt_housing_battery_consumed_ah_entries, 2)

            if entry.housing_battery_remaining_mins != globals.EMPTY_METRIC_VALUE:
                self._sum_housing_battery_remaining_mins += utils.try_parse_int(entry.housing_battery_remaining_mins)
                self._cnt_housing_battery_remaining_mins_entries += 1
                if self._summary_values[14] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[14] = entry.housing_battery_remaining_mins
                else:
                    self._summary_values[14] = \
                        round(
                            self._sum_housing_battery_remaining_mins / self._cnt_housing_battery_remaining_mins_entries)

        return entry

    def get_metadata_values(self):
        if len(self._log_entries) > 0:
            return self._log_entries[len(self._log_entries) - 1].get_values()
        else:
            return []

    def get_summary_headers(self):
        return globals.VICTRON_BLE_PLUGIN_SUMMARY_HEADERS.copy()

    def get_summary_values(self):
        return self._summary_values.copy()
