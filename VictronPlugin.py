from pyModbusTCP.client import ModbusClient

import Helper
from Plugin import Plugin

MODBUS_TCP_PORT = 502


class VictronEntry:
    def __init__(self, input_source_string, grid_power, generator_power, ac_input_voltage, ac_input_current,
                 ac_input_frequency, ve_bus_state_string, ac_consumption, battery_voltage,
                 battery_current, battery_power, battery_soc, battery_state_string,
                 pv_power, pv_current, starter_battery_voltage):
        self.input_source_string = input_source_string
        self.grid_power = grid_power
        self.generator_power = generator_power
        self.ac_input_voltage = ac_input_voltage
        self.ac_input_current = ac_input_current
        self.ac_input_frequency = ac_input_frequency
        self.ve_bus_state_string = ve_bus_state_string
        self.ac_consumption = ac_consumption
        self.battery_voltage = battery_voltage
        self.battery_current = battery_current
        self.battery_power = battery_power
        self.battery_soc = battery_soc
        self.battery_state_string = battery_state_string
        self.pv_power = pv_power
        self.pv_current = pv_current
        self.starter_battery_voltage = starter_battery_voltage

    def __str__(self):
        return Helper.get_comma_separated_string(self.get_values())

    def get_values(self):
        return [f'{self.input_source_string}', f'{self.grid_power}', f'{self.generator_power}',
                f'{self.ac_input_voltage}', f'{self.ac_input_current}', f'{self.ac_input_frequency}',
                f'{self.ve_bus_state_string}', f'{self.ac_consumption}', f'{self.battery_voltage}',
                f'{self.battery_current}', f'{self.battery_power}', f'{self.battery_soc}',
                f'{self.battery_state_string}',
                f'{self.pv_power}', f'{self.pv_current}', f'{self.starter_battery_voltage}']


class VictronPlugin(Plugin):
    log_entries = []

    def __init__(self, args):
        # invoking the __init__ of the parent class
        Plugin.__init__(self, args)

    def get_metadata_headers(self):
        return ['Active Input source', 'Grid 1 power (W)', 'Generator 1 power (W)',
                'AC Input 1 Voltage (V)', 'AC Input 1 Current (A)', 'AC Input 1 Frequency (Hz)',
                'VE.Bus State', 'AC Consumption (W)', 'Battery Voltage (V)', 'Battery Current (A)',
                'Battery Power (W)', 'Battery SOC', 'Battery state', 'PV Power (W)', 'PV Current (A)',
                'Starter Battery Voltage (V)']

    def take_snapshot(self):
        server_ip = f'{self.args.victron_server_ip}'
        server_port = MODBUS_TCP_PORT

        try:
            # TCP auto connect on modbus request, close after it
            c = ModbusClient(host=server_ip, port=server_port, unit_id=100, auto_open=True, auto_close=True)

            grid_power = int(c.read_holding_registers(820, 1)[0])
            generator_power = int(c.read_holding_registers(823, 1)[0])

            input_source_string = ''
            input_source = int(c.read_holding_registers(826, 1)[0])
            if input_source == 0:
                input_source_string = 'Unknown'
            elif input_source == 1:
                input_source_string = 'Grid'
            elif input_source == 2:
                input_source_string = 'Generator'
            elif input_source == 3:
                input_source_string = 'Shore Power'
            elif input_source == 240:
                input_source_string = 'Not Connected'

            ac_consumption = int(c.read_holding_registers(817, 1)[0])

            battery_state_string = ''
            battery_state = int(c.read_holding_registers(844, 1)[0])
            if battery_state == 0:
                battery_state_string = 'idle'
            elif battery_state == 1:
                battery_state_string = 'charging'
            elif battery_state == 2:
                battery_state_string = 'discharging'

            battery_voltage = int(c.read_holding_registers(840, 1)[0]) / 10
            battery_current = int(c.read_holding_registers(841, 1)[0]) / 10
            battery_power = int(c.read_holding_registers(842, 1)[0])
            battery_soc = int(c.read_holding_registers(843, 1)[0])
            pv_power = int(c.read_holding_registers(850, 1)[0])
            pv_current = int(c.read_holding_registers(851, 1)[0]) / 10

            # Get starter battery voltage
            c.unit_id = 223
            starter_battery_voltage = int(c.read_holding_registers(260, 1)[0]) / 100

            # Get VE.Bus metrics
            c.unit_id = 227
            ac_input_voltage = int(c.read_holding_registers(3, 1)[0]) / 10
            ac_input_current = int(c.read_holding_registers(6, 1)[0]) / 10
            ac_input_frequency = int(c.read_holding_registers(9, 1)[0]) / 100

            ve_bus_state_string = ''
            ve_bus_state = int(c.read_holding_registers(31, 1)[0])
            if ve_bus_state == 0:
                ve_bus_state_string = 'Off'
            elif ve_bus_state == 1:
                ve_bus_state_string = 'Low Power'
            elif ve_bus_state == 2:
                ve_bus_state_string = 'Fault'
            elif ve_bus_state == 3:
                ve_bus_state_string = 'Bulk'
            elif ve_bus_state == 4:
                ve_bus_state_string = 'Absorption'
            elif ve_bus_state == 5:
                ve_bus_state_string = 'Float'
            elif ve_bus_state == 6:
                ve_bus_state_string = 'Storage'
            elif ve_bus_state == 7:
                ve_bus_state_string = 'Equalize'
            elif ve_bus_state == 8:
                ve_bus_state_string = 'Passthru'
            elif ve_bus_state == 9:
                ve_bus_state_string = 'Inverting'
            elif ve_bus_state == 10:
                ve_bus_state_string = 'Power assist'
            elif ve_bus_state == 11:
                ve_bus_state_string = 'Power supply'
            elif ve_bus_state == 252:
                ve_bus_state_string = 'External control'

            Helper.console_out(f'Active Input source: {input_source_string}')
            Helper.console_out(f'Grid power: {grid_power} W')
            Helper.console_out(f'Generator power: {generator_power} W')
            Helper.console_out(f'AC input 1 {ac_input_voltage} VAC {ac_input_current} A {ac_input_frequency} Hz')
            Helper.console_out(f'VE.Bus State: {ve_bus_state_string}')
            Helper.console_out(f'AC Consumption: {ac_consumption} W AC')
            Helper.console_out(f'Battery voltage: {battery_voltage} VDC')
            Helper.console_out(f'Battery current: {battery_current} A')
            Helper.console_out(f'Battery power: {battery_power} W DC')
            Helper.console_out(f'Battery SOC: {battery_soc} %')
            Helper.console_out(f'Battery state: {battery_state_string}')
            Helper.console_out(f'PV power: {pv_power} W DC')
            Helper.console_out(f'PV current: {pv_current} A DC')
            Helper.console_out(f'Starter battery voltage: {starter_battery_voltage} V DC')

            entry = VictronEntry(input_source_string, grid_power, generator_power, ac_input_voltage,
                                 ac_input_current, ac_input_frequency, ve_bus_state_string, ac_consumption,
                                 battery_voltage, battery_current, battery_power, battery_soc, battery_state_string,
                                 pv_power, pv_current, starter_battery_voltage)
            self.log_entries.append(entry)
        except ValueError:
            Helper.console_out("Error with host or port params")

    def get_metadata_values(self):
        if len(self.log_entries) > 0:
            return self.log_entries[len(self.log_entries) - 1].get_values()
        else:
            return []

    def reset_entries(self):
        self.log_entries = []
