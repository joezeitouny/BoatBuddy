from pyModbusTCP.client import ModbusClient

from Plugin import Plugin

TCP_PORT = 502


class VictronPlugin(Plugin):
    def __init__(self, args):
        # invoking the __init__ of the parent class
        Plugin.__init__(self, args)

        self.metadata_headers = ['Active Input source', 'Grid 1 power (W)', 'Generator 1 power (W)',
                                 'AC Input 1 Voltage (V)', 'AC Input 1 Current (A)', 'AC Input 1 Frequency (Hz)',
                                 'VE.Bus State', 'AC Consumption (W)', 'Battery Voltage (V)', 'Battery Current (A)',
                                 'Battery Power (W)', 'Battery SOC', 'Battery state', 'PV Power (W)', 'PV Current (A)',
                                 'Starter Battery Voltage (V)']

    def get_metadata_values(self, print_func):
        server_ip = self.args[0]
        server_port = TCP_PORT

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

            print_func(f'Active Input source: {input_source_string}')
            print_func(f'Grid power: {grid_power} W')
            print_func(f'Generator power: {generator_power} W')
            print_func(f'AC input 1 {ac_input_voltage} VAC {ac_input_current} A {ac_input_frequency} Hz')
            print_func(f'VE.Bus State: {ve_bus_state_string}')
            print_func(f'AC Consumption: {ac_consumption} W AC')
            print_func(f'Battery voltage: {battery_voltage} VDC')
            print_func(f'Battery current: {battery_current} A')
            print_func(f'Battery power: {battery_power} W DC')
            print_func(f'Battery SOC: {battery_soc} %')
            print_func(f'Battery state: {battery_state_string}')
            print_func(f'PV power: {pv_power} W DC')
            print_func(f'PV current: {pv_current} A DC')

            print_func(f'Starter battery voltage: {starter_battery_voltage} V DC')

            self.metadata_values = [f'{input_source_string}', f'{grid_power}', f'{generator_power}',
                                    f'{ac_input_voltage}', f'{ac_input_current}', f'{ac_input_frequency}',
                                    f'{ve_bus_state_string}', f'{ac_consumption}', f'{battery_voltage}',
                                    f'{battery_current}', f'{battery_power}', f'{battery_soc}',
                                    f'{battery_state_string}',
                                    f'{pv_power}', f'{pv_current}', f'{starter_battery_voltage}']

        except ValueError:
            print_func("Error with host or port params")

        return self.metadata_values
