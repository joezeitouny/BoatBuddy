import threading
import time

import numpy as np
from events import Events
from pyModbusTCP.client import ModbusClient

from BoatBuddy import globals, utils
from BoatBuddy.generic_plugin import GenericPlugin, PluginStatus


class VictronModbusTCPPluginEvents(Events):
    __events__ = ('on_connect', 'on_disconnect',)


class VictronModbusTCPEntry:
    def __init__(self, input_source_string, grid_power, generator_power, ac_input_voltage, ac_input_current,
                 ac_input_frequency, ve_bus_state_string, ac_consumption, battery_voltage,
                 battery_current, battery_power, battery_soc, battery_state_string,
                 pv_power, pv_current, starter_battery_voltage, tank1_level, tank1_type, tank2_level, tank2_type):
        self._input_source_string = input_source_string
        self._grid_power = grid_power
        self._generator_power = generator_power
        self._ac_input_voltage = ac_input_voltage
        self._ac_input_current = ac_input_current
        self._ac_input_frequency = ac_input_frequency
        self._ve_bus_state_string = ve_bus_state_string
        self._ac_consumption = ac_consumption
        self._battery_voltage = battery_voltage
        self._battery_current = battery_current
        self._battery_power = battery_power
        self._battery_soc = battery_soc
        self._battery_state_string = battery_state_string
        self._pv_power = pv_power
        self._pv_current = pv_current
        self._starter_battery_voltage = starter_battery_voltage
        self._tank1_level = tank1_level
        self._tank1_type = tank1_type
        self._tank2_level = tank2_level
        self._tank2_type = tank2_type

    def __str__(self):
        return utils.get_comma_separated_string(self.get_values())

    def get_values(self):
        return [f'{self._input_source_string}', f'{self._grid_power}', f'{self._generator_power}',
                f'{self._ac_input_voltage}', f'{self._ac_input_current}', f'{self._ac_input_frequency}',
                f'{self._ve_bus_state_string}', f'{self._ac_consumption}', f'{self._battery_voltage}',
                f'{self._battery_current}', f'{self._battery_power}', f'{self._battery_soc}',
                f'{self._battery_state_string}',
                f'{self._pv_power}', f'{self._pv_current}', f'{self._starter_battery_voltage}',
                f'{self._tank1_level}', f'{self._tank1_type}', f'{self._tank2_level}', f'{self._tank2_type}']

    def get_battery_voltage(self):
        return self._battery_voltage

    def get_battery_current(self):
        return self._battery_current

    def get_battery_power(self):
        return self._battery_power

    def get_pv_power(self):
        return self._pv_power

    def get_pv_current(self):
        return self._pv_current

    def get_starter_battery_voltage(self):
        return self._starter_battery_voltage

    def get_ac_consumption_power(self):
        return self._ac_consumption

    def get_tank1_level(self):
        return self._tank1_level

    def get_tank1_type(self):
        return self._tank1_type

    def get_tank2_level(self):
        return self._tank2_level

    def get_tank2_type(self):
        return self._tank2_type


class VictronModbusTCPPlugin(GenericPlugin):
    _events = None

    def __init__(self, options, log_manager):
        # invoking the __init__ of the parent class
        GenericPlugin.__init__(self, options, log_manager)

        # Instance metrics
        self._grid_power = globals.EMPTY_METRIC_VALUE
        self._generator_power = globals.EMPTY_METRIC_VALUE
        self._input_source_string = globals.EMPTY_METRIC_VALUE
        self._ac_consumption = globals.EMPTY_METRIC_VALUE
        self._battery_state_string = globals.EMPTY_METRIC_VALUE
        self._battery_voltage = globals.EMPTY_METRIC_VALUE
        self._battery_current = globals.EMPTY_METRIC_VALUE
        self._battery_power = globals.EMPTY_METRIC_VALUE
        self._battery_soc = globals.EMPTY_METRIC_VALUE
        self._pv_power = globals.EMPTY_METRIC_VALUE
        self._pv_current = globals.EMPTY_METRIC_VALUE
        self._starter_battery_voltage = globals.EMPTY_METRIC_VALUE
        self._ac_input_voltage = globals.EMPTY_METRIC_VALUE
        self._ac_input_current = globals.EMPTY_METRIC_VALUE
        self._ac_input_frequency = globals.EMPTY_METRIC_VALUE
        self._ve_bus_state_string = globals.EMPTY_METRIC_VALUE
        self._tank1_level = globals.EMPTY_METRIC_VALUE
        self._tank1_type_string = globals.EMPTY_METRIC_VALUE
        self._tank2_level = globals.EMPTY_METRIC_VALUE
        self._tank2_type_string = globals.EMPTY_METRIC_VALUE
        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]
        self._sum_housing_battery_voltage = 0
        self._cnt_housing_battery_voltage_entries = 0
        self._sum_housing_battery_current = 0
        self._cnt_housing_battery_current_entries = 0
        self._sum_housing_battery_power = 0
        self._cnt_housing_battery_power_entries = 0
        self._sum_pv_power = 0
        self._cnt_pv_power_entries = 0
        self._sum_pv_current = 0
        self._cnt_pv_current_entries = 0
        self._sum_starter_battery_voltage = 0
        self._cnt_starter_battery_voltage_entries = 0
        self._sum_ac_consumption_power = 0
        self._cnt_ac_consumption_power_entries = 0
        self._sum_tank1_level = 0
        self._cnt_tank1_level_entries = 0
        self._sum_tank2_level = 0
        self._cnt_tank2_level_entries = 0

        # Other instance variables
        self._plugin_status = PluginStatus.STARTING
        self._exit_signal = threading.Event()
        self._timer = threading.Timer(globals.VICTRON_MODBUS_TCP_TIMER_INTERVAL, self._main_loop)
        self._timer.start()
        self._log_manager.info('Victron Modbus TCP module successfully started!')

    def reset_instance_metrics(self):
        self._grid_power = globals.EMPTY_METRIC_VALUE
        self._generator_power = globals.EMPTY_METRIC_VALUE
        self._input_source_string = globals.EMPTY_METRIC_VALUE
        self._ac_consumption = globals.EMPTY_METRIC_VALUE
        self._battery_state_string = globals.EMPTY_METRIC_VALUE
        self._battery_voltage = globals.EMPTY_METRIC_VALUE
        self._battery_current = globals.EMPTY_METRIC_VALUE
        self._battery_power = globals.EMPTY_METRIC_VALUE
        self._battery_soc = globals.EMPTY_METRIC_VALUE
        self._pv_power = globals.EMPTY_METRIC_VALUE
        self._pv_current = globals.EMPTY_METRIC_VALUE
        self._starter_battery_voltage = globals.EMPTY_METRIC_VALUE
        self._ac_input_voltage = globals.EMPTY_METRIC_VALUE
        self._ac_input_current = globals.EMPTY_METRIC_VALUE
        self._ac_input_frequency = globals.EMPTY_METRIC_VALUE
        self._ve_bus_state_string = globals.EMPTY_METRIC_VALUE
        self._tank1_level = globals.EMPTY_METRIC_VALUE
        self._tank1_type_string = globals.EMPTY_METRIC_VALUE
        self._tank2_level = globals.EMPTY_METRIC_VALUE
        self._tank2_type_string = globals.EMPTY_METRIC_VALUE
        self._summary_values = [globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE,
                                globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE, globals.EMPTY_METRIC_VALUE]
        self._sum_housing_battery_voltage = 0
        self._cnt_housing_battery_voltage_entries = 0
        self._sum_housing_battery_current = 0
        self._cnt_housing_battery_current_entries = 0
        self._sum_housing_battery_power = 0
        self._cnt_housing_battery_power_entries = 0
        self._sum_pv_power = 0
        self._cnt_pv_power_entries = 0
        self._sum_pv_current = 0
        self._cnt_pv_current_entries = 0
        self._sum_starter_battery_voltage = 0
        self._cnt_starter_battery_voltage_entries = 0
        self._sum_ac_consumption_power = 0
        self._cnt_ac_consumption_power_entries = 0
        self._sum_tank1_level = 0
        self._cnt_tank1_level_entries = 0
        self._sum_tank2_level = 0
        self._cnt_tank2_level_entries = 0

    def _main_loop(self):
        if self._exit_signal.is_set():
            self._plugin_status = PluginStatus.DOWN
            self._log_manager.info('Victron Modbus TCP plugin instance is ready to be destroyed')
            return

        server_ip = f'{self._options.victron_modbus_tcp_server_ip}'
        server_port = self._options.victron_modbus_tcp_port

        try:
            # TCP auto connect on modbus request, close after it
            c = ModbusClient(host=server_ip, port=server_port, unit_id=100, auto_open=True, auto_close=True)

            # Try to make a test inquiry to the system before proceeding any further
            if c.read_holding_registers(820, 1) is None:
                raise ValueError('Modbus TCP server is unreachable')

            if self._plugin_status != PluginStatus.RUNNING:
                self._log_manager.info(f'Connection to Victron Modbus TCP system on {server_ip} is established')

                self._plugin_status = PluginStatus.RUNNING

                self.reset_instance_metrics()

                if self._events:
                    self._events.on_connect()

            try:
                self._grid_power = utils.try_parse_int(c.read_holding_registers(820, 1)[0])
                self._generator_power = utils.try_parse_int(np.int16(c.read_holding_registers(823, 1)[0]))

                self._input_source_string = ''
                input_source = utils.try_parse_int(c.read_holding_registers(826, 1)[0])
                if input_source == 0:
                    self._input_source_string = 'Unknown'
                elif input_source == 1:
                    self._input_source_string = 'Grid'
                elif input_source == 2:
                    self._input_source_string = 'Generator'
                elif input_source == 3:
                    self._input_source_string = 'Shore Power'
                elif input_source == 240:
                    self._input_source_string = 'Not Connected'

                self._ac_consumption = utils.try_parse_int(c.read_holding_registers(817, 1)[0])

                self._battery_state_string = ''
                battery_state = utils.try_parse_int(c.read_holding_registers(844, 1)[0])
                if battery_state == 0:
                    self._battery_state_string = 'idle'
                elif battery_state == 1:
                    self._battery_state_string = 'charging'
                elif battery_state == 2:
                    self._battery_state_string = 'discharging'

                self._battery_voltage = utils.try_parse_int(c.read_holding_registers(840, 1)[0]) / 10
                self._battery_current = utils.try_parse_int(np.int16(c.read_holding_registers(841, 1)[0])) / 10
                self._battery_power = utils.try_parse_int(np.int16(c.read_holding_registers(842, 1)[0]))
                self._battery_soc = utils.try_parse_int(c.read_holding_registers(843, 1)[0])
                self._pv_power = utils.try_parse_int(c.read_holding_registers(850, 1)[0])
                self._pv_current = utils.try_parse_int(np.int16(c.read_holding_registers(851, 1)[0])) / 10

                # Get starter battery voltage
                c.unit_id = 223
                self._starter_battery_voltage = utils.try_parse_int(c.read_holding_registers(260, 1)[0]) / 100

                # Get VE.Bus metrics
                c.unit_id = 227
                self._ac_input_voltage = utils.try_parse_int(c.read_holding_registers(3, 1)[0]) / 10
                self._ac_input_current = utils.try_parse_int(np.int16(c.read_holding_registers(6, 1)[0])) / 10
                self._ac_input_frequency = utils.try_parse_int(c.read_holding_registers(9, 1)[0]) / 100

                self._ve_bus_state_string = ''
                ve_bus_state = utils.try_parse_int(c.read_holding_registers(31, 1)[0])
                if ve_bus_state == 0:
                    self._ve_bus_state_string = 'Off'
                elif ve_bus_state == 1:
                    self._ve_bus_state_string = 'Low Power'
                elif ve_bus_state == 2:
                    self._ve_bus_state_string = 'Fault'
                elif ve_bus_state == 3:
                    self._ve_bus_state_string = 'Bulk'
                elif ve_bus_state == 4:
                    self._ve_bus_state_string = 'Absorption'
                elif ve_bus_state == 5:
                    self._ve_bus_state_string = 'Float'
                elif ve_bus_state == 6:
                    self._ve_bus_state_string = 'Storage'
                elif ve_bus_state == 7:
                    self._ve_bus_state_string = 'Equalize'
                elif ve_bus_state == 8:
                    self._ve_bus_state_string = 'Passthru'
                elif ve_bus_state == 9:
                    self._ve_bus_state_string = 'Inverting'
                elif ve_bus_state == 10:
                    self._ve_bus_state_string = 'Power assist'
                elif ve_bus_state == 11:
                    self._ve_bus_state_string = 'Power supply'
                elif ve_bus_state == 252:
                    self._ve_bus_state_string = 'External control'

                c.unit_id = 20
                self._tank1_level = utils.try_parse_int(utils.try_parse_int(c.read_holding_registers(3004, 1)[0]) / 10)
                tank1_type = utils.try_parse_int(c.read_holding_registers(3003, 1)[0])
                self._tank1_type_string = ''
                # 0=Fuel;1=Fresh water;2=Waste water;3=Live well;4=Oil;5=Black water (sewage);
                # 6=Gasoline;7=Diesel;8=LPG;9=LNG;10=Hydraulic oil;11=Raw water
                if tank1_type == 0:
                    self._tank1_type_string = 'Fuel'
                elif tank1_type == 1:
                    self._tank1_type_string = 'Fresh water'
                elif tank1_type == 2:
                    self._tank1_type_string = 'Waste water'
                elif tank1_type == 3:
                    self._tank1_type_string = 'Live well'
                elif tank1_type == 4:
                    self._tank1_type_string = 'Oil'
                elif tank1_type == 5:
                    self._tank1_type_string = 'Black water (sewage)'
                elif tank1_type == 6:
                    self._tank1_type_string = 'Gasoline'
                elif tank1_type == 7:
                    self._tank1_type_string = 'Diesel'
                elif tank1_type == 8:
                    self._tank1_type_string = 'LPG'
                elif tank1_type == 9:
                    self._tank1_type_string = 'LNG'
                elif tank1_type == 10:
                    self._tank1_type_string = 'Hydraulic oil'
                elif tank1_type == 11:
                    self._tank1_type_string = 'Raw water'

                c.unit_id = 21
                self._tank2_level = utils.try_parse_int(utils.try_parse_int(c.read_holding_registers(3004, 1)[0]) / 10)
                tank2_type = utils.try_parse_int(c.read_holding_registers(3003, 1)[0])
                self._tank2_type_string = ''
                if tank2_type == 0:
                    self._tank2_type_string = 'Fuel'
                elif tank2_type == 1:
                    self._tank2_type_string = 'Fresh water'
                elif tank2_type == 2:
                    self._tank2_type_string = 'Waste water'
                elif tank2_type == 3:
                    self._tank2_type_string = 'Live well'
                elif tank2_type == 4:
                    self._tank2_type_string = 'Oil'
                elif tank2_type == 5:
                    self._tank2_type_string = 'Black water (sewage)'
                elif tank2_type == 6:
                    self._tank2_type_string = 'Gasoline'
                elif tank2_type == 7:
                    self._tank2_type_string = 'Diesel'
                elif tank2_type == 8:
                    self._tank2_type_string = 'LPG'
                elif tank2_type == 9:
                    self._tank2_type_string = 'LNG'
                elif tank2_type == 10:
                    self._tank2_type_string = 'Hydraulic oil'
                elif tank2_type == 11:
                    self._tank2_type_string = 'Raw water'
            except Exception as e:
                self._handle_connection_exception(e)
        except Exception as e:
            self._handle_connection_exception(e)

        # sleep for 1 second
        time.sleep(globals.VICTRON_MODBUS_TCP_SAMPLING_RATE)

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
        entry = VictronModbusTCPEntry(self._input_source_string, self._grid_power, self._generator_power,
                                      self._ac_input_voltage, self._ac_input_current, self._ac_input_frequency,
                                      self._ve_bus_state_string, self._ac_consumption, self._battery_voltage,
                                      self._battery_current, self._battery_power, self._battery_soc,
                                      self._battery_state_string, self._pv_power, self._pv_current,
                                      self._starter_battery_voltage, self._tank1_level, self._tank1_type_string,
                                      self._tank2_level, self._tank2_type_string)

        if store_entry:
            self._log_manager.debug(f'Adding new Victron Modbus TCP entry')
            self._log_manager.debug(f'Active Input source: {self._input_source_string} ' +
                                    f'Grid Power: {self._grid_power} W ' +
                                    f'Generator Power: {self._generator_power} W ' +
                                    f'AC Consumption: {self._ac_consumption} W')
            self._log_manager.debug(f'AC input 1 {self._ac_input_voltage} V {self._ac_input_current} A ' +
                                    f'{self._ac_input_frequency} Hz ' +
                                    f'State: {self._ve_bus_state_string}')
            self._log_manager.debug(
                f'Housing battery stats {self._battery_voltage} V  {self._battery_current} A {self._battery_power} W ' +
                f'{self._battery_soc} % {self._battery_state_string}')
            self._log_manager.debug(f'PV {self._pv_power} W {self._pv_current} A')
            self._log_manager.debug(f'Starter battery voltage: {self._starter_battery_voltage} V')
            self._log_manager.debug(f'Tank 1 Level: {self._tank1_level} Type: {self._tank1_type_string}')
            self._log_manager.debug(f'Tank 2 Level: {self._tank2_level} Type: {self._tank2_type_string}')

            self._log_entries.append(entry)

            # Calculate extremes and averages
            if entry.get_battery_voltage() != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[0] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[0] = entry.get_battery_voltage()
                else:
                    self._summary_values[0] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.get_battery_voltage()),
                                                 self._summary_values[0])

                if self._summary_values[1] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[1] = entry.get_battery_voltage()
                else:
                    self._summary_values[1] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.get_battery_voltage()),
                                                  self._summary_values[1])

                self._sum_housing_battery_voltage += utils.try_parse_float(entry.get_battery_voltage())
                self._cnt_housing_battery_voltage_entries += 1
                if self._summary_values[2] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[2] = entry.get_battery_voltage()
                else:
                    self._summary_values[2] = \
                        round(self._sum_housing_battery_voltage / self._cnt_housing_battery_voltage_entries, 2)

            if entry.get_battery_current() != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[3] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[3] = entry.get_battery_current()
                else:
                    self._summary_values[3] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.get_battery_current()),
                                                 self._summary_values[3])

                if self._summary_values[4] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[4] = entry.get_battery_current()
                else:
                    self._summary_values[4] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.get_battery_current()),
                                                  self._summary_values[4])

                self._sum_housing_battery_current += utils.try_parse_float(entry.get_battery_current())
                self._cnt_housing_battery_current_entries += 1
                if self._summary_values[5] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[5] = entry.get_battery_current()
                else:
                    self._summary_values[5] = \
                        round(self._sum_housing_battery_current / self._cnt_housing_battery_current_entries, 2)

            if entry.get_battery_power() != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[6] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[6] = entry.get_battery_power()
                else:
                    self._summary_values[6] = \
                        utils.get_biggest_number(utils.try_parse_int(entry.get_battery_power()),
                                                 self._summary_values[6])

                if self._summary_values[7] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[7] = entry.get_battery_power()
                else:
                    self._summary_values[7] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.get_battery_power()),
                                                  self._summary_values[7])

                self._sum_housing_battery_power += utils.try_parse_int(entry.get_battery_power())
                self._cnt_housing_battery_power_entries += 1
                if self._summary_values[8] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[8] = entry.get_battery_power()
                else:
                    self._summary_values[8] = \
                        round(self._sum_housing_battery_power / self._cnt_housing_battery_power_entries)

            if entry.get_pv_power() != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[9] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[9] = entry.get_pv_power()
                else:
                    self._summary_values[9] = \
                        utils.get_biggest_number(utils.try_parse_int(entry.get_pv_power()),
                                                 self._summary_values[9])

                self._sum_pv_power += utils.try_parse_int(entry.get_pv_power())
                self._cnt_pv_power_entries += 1
                if self._summary_values[10] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[10] = entry.get_pv_power()
                else:
                    self._summary_values[10] = round(self._sum_pv_power / self._cnt_pv_power_entries)

            if entry.get_pv_current() != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[11] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[11] = entry.get_pv_current()
                else:
                    self._summary_values[11] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.get_pv_current()),
                                                 self._summary_values[11])

                self._sum_pv_current += utils.try_parse_float(entry.get_pv_current())
                self._cnt_pv_current_entries += 1
                if self._summary_values[12] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[12] = entry.get_pv_current()
                else:
                    self._summary_values[12] = round(self._sum_pv_current / self._cnt_pv_current_entries, 2)

            if entry.get_starter_battery_voltage() != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[13] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[13] = entry.get_starter_battery_voltage()
                else:
                    self._summary_values[13] = \
                        utils.get_biggest_number(utils.try_parse_float(entry.get_starter_battery_voltage()),
                                                 self._summary_values[13])

                if self._summary_values[14] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[14] = entry.get_starter_battery_voltage()
                else:
                    self._summary_values[14] = \
                        utils.get_smallest_number(utils.try_parse_float(entry.get_starter_battery_voltage()),
                                                  self._summary_values[14])

                self._sum_starter_battery_voltage += utils.try_parse_float(entry.get_starter_battery_voltage())
                self._cnt_starter_battery_voltage_entries += 1
                if self._summary_values[15] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[15] = entry.get_starter_battery_voltage()
                else:
                    self._summary_values[15] = \
                        round(self._sum_starter_battery_voltage / self._cnt_starter_battery_voltage_entries, 2)

            if entry.get_ac_consumption_power() != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[16] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[16] = entry.get_ac_consumption_power()
                else:
                    self._summary_values[16] = \
                        utils.get_biggest_number(utils.try_parse_int(entry.get_ac_consumption_power()),
                                                 self._summary_values[16])

                self._sum_ac_consumption_power += utils.try_parse_int(entry.get_ac_consumption_power())
                self._cnt_ac_consumption_power_entries += 1
                if self._summary_values[17] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[17] = entry.get_ac_consumption_power()
                else:
                    self._summary_values[17] = \
                        round(self._sum_ac_consumption_power / self._cnt_ac_consumption_power_entries)

            if entry.get_tank1_level() != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[18] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[18] = entry.get_tank1_level()
                else:
                    self._summary_values[18] = \
                        utils.get_biggest_number(utils.try_parse_int(entry.get_tank1_level()),
                                                 self._summary_values[18])

                if self._summary_values[19] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[19] = entry.get_tank1_level()
                else:
                    self._summary_values[19] = \
                        utils.get_smallest_number(utils.try_parse_int(entry.get_tank1_level()),
                                                  self._summary_values[19])

                self._sum_tank1_level += utils.try_parse_int(entry.get_tank1_level())
                self._cnt_tank1_level_entries += 1
                if self._summary_values[20] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[20] = entry.get_tank1_level()
                else:
                    self._summary_values[20] = \
                        round(self._sum_tank1_level / self._cnt_tank1_level_entries)

            if entry.get_tank2_level() != globals.EMPTY_METRIC_VALUE:
                if self._summary_values[21] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[21] = entry.get_tank2_level()
                else:
                    self._summary_values[21] = \
                        utils.get_biggest_number(utils.try_parse_int(entry.get_tank2_level()),
                                                 self._summary_values[21])

                if self._summary_values[22] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[22] = entry.get_tank2_level()
                else:
                    self._summary_values[22] = \
                        utils.get_smallest_number(utils.try_parse_int(entry.get_tank2_level()),
                                                  self._summary_values[22])

                self._sum_tank2_level += utils.try_parse_int(entry.get_tank2_level())
                self._cnt_tank2_level_entries += 1
                if self._summary_values[23] == globals.EMPTY_METRIC_VALUE:
                    self._summary_values[23] = entry.get_tank2_level()
                else:
                    self._summary_values[23] = \
                        round(self._sum_tank2_level / self._cnt_tank2_level_entries)

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
        self._log_manager.info("Victron Modbus TCP plugin worker thread notified...")

    def get_summary_headers(self):
        return globals.VICTRON_MODBUS_TCP_PLUGIN_SUMMARY_HEADERS.copy()

    def get_summary_values(self):
        return self._summary_values.copy()

    def get_status(self) -> PluginStatus:
        return self._plugin_status

    def register_for_events(self, events):
        self._events = events
