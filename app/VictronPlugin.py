from pyModbusTCP.client import ModbusClient

import config
from app import Helper
from app.Plugin import Plugin


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

    def get_battery_voltage(self):
        return self.battery_voltage

    def get_battery_current(self):
        return self.battery_current

    def get_battery_power(self):
        return self.battery_power

    def get_pv_power(self):
        return self.pv_power

    def get_pv_current(self):
        return self.pv_current

    def get_starter_battery_voltage(self):
        return self.starter_battery_voltage

    def get_ac_consumption_power(self):
        return self.ac_consumption


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
        server_port = config.MODBUS_TCP_PORT

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

            Helper.console_out(f'Active Input source: {input_source_string} Grid Power: {grid_power} W ' +
                               f'Generator Power: {generator_power} W AC Consumption: {ac_consumption} W')
            Helper.console_out(f'AC input 1 {ac_input_voltage} V {ac_input_current} A {ac_input_frequency} Hz ' +
                               f'State: {ve_bus_state_string}')
            Helper.console_out(f'Housing battery stats {battery_voltage} V  {battery_current} A {battery_power} W ' +
                               f'{battery_soc} % {battery_state_string}')
            Helper.console_out(f'PV {pv_power} W {pv_current} A')
            Helper.console_out(f'Starter battery voltage: {starter_battery_voltage} V')

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

    def finalize(self):
        print('Victron plugin worker terminated')

    def get_summary_headers(self):
        return ["Housing battery max voltage (V)", "Housing battery min voltage (V)",
                "Housing battery average voltage (V)", "Housing battery max current (A)",
                "Housing battery average current (A)", "Housing battery max power (W)",
                "Housing battery average power (W)",
                "PV max power (W)", "PV average power",
                "PV max current (A)", "PV average current (A)",
                "Starter battery max voltage (V)", "Starter battery min voltage (V)",
                "Starter battery average voltage", "AC Consumption max (W)", "AC Consumption average (W)"]

    def get_summary_values(self):
        log_summary_list = []

        if len(self.log_entries) > 0:
            first_entry = self.log_entries[0]
            last_entry = self.log_entries[len(self.log_entries) - 1]

            # Calculate extremes and averages
            housing_battery_max_voltage = 0
            housing_battery_min_voltage = 0
            sum_housing_battery_voltage = 0
            housing_battery_max_current = 0
            sum_housing_battery_current = 0
            housing_battery_max_power = 0
            sum_housing_battery_power = 0
            pv_max_power = 0
            sum_pv_power = 0
            pv_max_current = 0
            sum_pv_current = 0
            starter_battery_max_voltage = 0
            starter_battery_min_voltage = 0
            sum_starter_battery_voltage = 0
            ac_consumption_max_power = 0
            sum_ac_consumption_power = 0
            count = len(self.log_entries)
            for entry in self.log_entries:
                # Sum up all values that will be averaged later
                sum_housing_battery_voltage += float(entry.get_battery_voltage())
                sum_housing_battery_current += int(entry.get_battery_current())
                sum_housing_battery_power += float(entry.get_battery_power())
                sum_pv_power += float(entry.get_pv_power())
                sum_pv_current += float(entry.get_pv_current())
                sum_starter_battery_voltage += float(entry.get_starter_battery_voltage())
                sum_ac_consumption_power += float(entry.get_ac_consumption_power())

                # Collect extremes
                housing_battery_max_voltage = Helper.get_biggest_number(float(entry.get_battery_voltage()),
                                                                        housing_battery_max_voltage)
                if housing_battery_min_voltage == 0:
                    housing_battery_min_voltage = float(entry.get_battery_voltage())
                else:
                    housing_battery_min_voltage = Helper.get_smallest_number(float(entry.get_battery_voltage()),
                                                                             housing_battery_min_voltage)
                housing_battery_max_current = Helper.get_biggest_number(float(entry.get_battery_current()),
                                                                        housing_battery_max_current)
                housing_battery_max_power = Helper.get_biggest_number(float(entry.get_battery_power()),
                                                                      housing_battery_max_power)
                pv_max_power = Helper.get_biggest_number(float(entry.get_pv_power()), pv_max_power)
                pv_max_current = Helper.get_biggest_number(float(entry.get_pv_current()), pv_max_current)
                starter_battery_max_voltage = Helper.get_biggest_number(float(entry.get_starter_battery_voltage()),
                                                                        starter_battery_max_voltage)
                if starter_battery_min_voltage == 0:
                    starter_battery_min_voltage = float(entry.get_starter_battery_voltage())
                else:
                    starter_battery_min_voltage = Helper.get_smallest_number(float(entry.get_starter_battery_voltage()),
                                                                             starter_battery_min_voltage)
                ac_consumption_max_power = Helper.get_biggest_number(float(entry.get_ac_consumption_power()),
                                                                     ac_consumption_max_power)

            log_summary_list.append(housing_battery_max_voltage)
            log_summary_list.append(housing_battery_min_voltage)
            log_summary_list.append(round(sum_housing_battery_voltage / count, 2))
            log_summary_list.append(housing_battery_max_current)
            log_summary_list.append(round(sum_housing_battery_current / count, 2))
            log_summary_list.append(housing_battery_max_power)
            log_summary_list.append(round(sum_housing_battery_power / count))
            log_summary_list.append(pv_max_power)
            log_summary_list.append(round(sum_pv_power / count))
            log_summary_list.append(pv_max_current)
            log_summary_list.append(round(sum_pv_current / count, 1))
            log_summary_list.append(starter_battery_max_voltage)
            log_summary_list.append(starter_battery_min_voltage)
            log_summary_list.append(round(sum_starter_battery_voltage / count, 2))
            log_summary_list.append(ac_consumption_max_power)
            log_summary_list.append(round(sum_ac_consumption_power / count))

        return log_summary_list
