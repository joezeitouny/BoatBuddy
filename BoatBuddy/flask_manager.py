import time
import webbrowser

from flask import render_template, jsonify
from rich.console import Console

from BoatBuddy import app
from BoatBuddy import utils, globals
from BoatBuddy.database_manager import DatabaseManager
from BoatBuddy.email_manager import EmailManager
from BoatBuddy.generic_plugin import PluginStatus
from BoatBuddy.log_manager import LogManager
from BoatBuddy.notifications_manager import NotificationsManager
from BoatBuddy.plugin_manager import PluginManager, PluginManagerStatus
from BoatBuddy.sound_manager import SoundManager, SoundType


class ApplicationModules:
    def __init__(self, options, log_manager: LogManager, sound_manager: SoundManager, email_manager: EmailManager,
                 notifications_manager: NotificationsManager, plugin_manager: PluginManager,
                 database_manager: DatabaseManager):
        self._options = options
        self._log_manager = log_manager
        self._sound_manager = sound_manager
        self._email_manager = email_manager
        self._notifications_manager = notifications_manager
        self._plugin_manager = plugin_manager
        self._database_manager = database_manager

    def get_options(self):
        return self._options

    def get_log_manager(self) -> LogManager:
        return self._log_manager

    def get_sound_manager(self) -> SoundManager:
        return self._sound_manager

    def get_email_manager(self) -> EmailManager:
        return self._email_manager

    def get_notifications_manager(self) -> NotificationsManager:
        return self._notifications_manager

    def get_plugin_manager(self) -> PluginManager:
        return self._plugin_manager

    def get_database_manager(self) -> DatabaseManager:
        return self._database_manager


application_modules: ApplicationModules


class FlaskManager:
    def __init__(self, options):
        self._options = options

        # Create a console instance
        _console = Console()
        _console.print(f'[bright_yellow]Application is starting up. Please wait...[/bright_yellow]')

        with _console.status('[bold bright_yellow]Loading logging module...[/bold bright_yellow]') as status:
            time.sleep(0.2)
            _log_manager = LogManager(self._options)
            _console.print(f'[green]Loading logging module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading sound module...[/bold bright_yellow]'):
            time.sleep(0.2)
            _sound_manager = SoundManager(self._options, _log_manager)
            _console.print(f'[green]Loading sound module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading email module...[/bold bright_yellow]'):
            time.sleep(0.2)
            _email_manager = EmailManager(self._options, _log_manager)
            _console.print(f'[green]Loading email module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading notifications module...[/bold bright_yellow]'):
            time.sleep(0.2)
            _notifications_manager = NotificationsManager(self._options, _log_manager, _sound_manager,
                                                               _email_manager)
            _console.print(f'[green]Loading notifications module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading plugins module...[/bold bright_yellow]'):
            time.sleep(0.2)
            _plugin_manager = PluginManager(self._options, _log_manager, _notifications_manager, _sound_manager,
                                            _email_manager)
            _console.print(f'[green]Loading plugins module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading database module...[/bold bright_yellow]'):
            time.sleep(0.2)
            _database_manager = DatabaseManager(self._options, _log_manager, _plugin_manager, _notifications_manager)
            _console.print(f'[green]Loading database module...Done[/green]')

        with _console.status(f'[bold bright_yellow]Firing up console UI...[/bold bright_yellow]'):
            time.sleep(0.2)
            # Play the application started chime
            _sound_manager.play_sound_async(SoundType.APPLICATION_STARTED)
            _console.print(f'[green]Firing up web UI...Done[/green]')

        global application_modules
        application_modules = ApplicationModules(self._options, _log_manager, _sound_manager, _email_manager,
                                                 _notifications_manager, _plugin_manager, _database_manager)

        webbrowser.open('http://127.0.0.1:5001')
        app.run(debug=False, host='0.0.0.0', port=5001)


def get_plugin_status_str(plugin_status: PluginStatus):
    plugin_status_str = ''
    if plugin_status == PluginStatus.DOWN:
        plugin_status_str = '(Down)'
    elif plugin_status == PluginStatus.STARTING:
        plugin_status_str = '(Starting)'
    elif plugin_status == PluginStatus.RUNNING:
        plugin_status_str = '(Running)'
    return plugin_status_str


def get_colour_from_status(plugin_status: PluginStatus):
    colour = 'default'
    if plugin_status == PluginStatus.DOWN:
        colour = 'red'
    elif plugin_status == PluginStatus.STARTING:
        colour = 'bright_yellow'
    elif plugin_status == PluginStatus.RUNNING:
        colour = 'green'

    return colour


@app.route('/')
def index():
    # Get application name and version
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()
    session_run_mode = str(application_modules.get_options().session_run_mode).lower()

    return render_template('index.html', application_name=application_name, application_version=application_version,
                           session_run_mode=session_run_mode)


@app.route('/toggle_session')
def start_stop_session():
    if not str(application_modules.get_options().session_run_mode).lower() == globals.SessionRunMode.MANUAL.value:
        return

    if application_modules.get_plugin_manager().get_status() == PluginManagerStatus.IDLE:
        application_modules.get_plugin_manager().start_session()
    elif application_modules.get_plugin_manager().get_status() == PluginManagerStatus.SESSION_ACTIVE:
        application_modules.get_plugin_manager().end_session()


@app.route('/data')
def get_data():
    curr_time = time.strftime("%H:%M:%S", time.localtime())
    status = application_modules.get_plugin_manager().get_status().value

    victron_module = False
    victron_status = ''
    victron_status_colour = ''
    active_input_source = 'N/A'
    ve_bus_state = 'N/A'
    housing_battery_state = 'N/A'
    housing_battery_current = 0
    pv_current = 0
    battery_soc = 0
    starter_battery_voltage = 0.0
    fuel_tank = 0
    water_tank = 0
    pv_max_power = 0
    pv_power = 0
    if application_modules.get_options().victron_module:
        victron_module = True
        pv_max_power = application_modules.get_options().victron_pv_max_power
        # Populate the victron layout
        plugin_status = application_modules.get_plugin_manager().get_victron_plugin_status()
        victron_status = get_plugin_status_str(plugin_status)
        victron_status_colour = get_colour_from_status(plugin_status)
        victron_metrics = application_modules.get_plugin_manager().get_victron_plugin_metrics()
        if victron_metrics and len(victron_metrics) > 0:
            active_input_source = victron_metrics[0]
            ve_bus_state = victron_metrics[6]
            housing_battery_state = victron_metrics[12]
            housing_battery_current = utils.try_parse_float(victron_metrics[9])
            battery_soc = utils.try_parse_int(victron_metrics[11])
            starter_battery_voltage = utils.try_parse_float(victron_metrics[15])
            pv_power = utils.try_parse_int(victron_metrics[13])
            pv_current = utils.try_parse_float(victron_metrics[14])
            fuel_tank = utils.try_parse_int(victron_metrics[16])
            water_tank = utils.try_parse_int(victron_metrics[18])

    # if self._options.gps_module and self._options.console_show_gps_plugin:
    #     gps_layout = Layout(name="gps")
    #     # Populate the NMEA layout
    #     plugin_status = self._plugin_manager.get_gps_plugin_status()
    #     formatted_plugin_status_str = self._get_formatted_plugin_status_str(plugin_status)
    #     border_style = self._get_border_style_from_status(plugin_status)
    #     ui_filtered_gps_plugin_metrics = utils.get_filtered_key_value_list(utils.get_key_value_list(
    #         globals.GPS_PLUGIN_METADATA_HEADERS, self._plugin_manager.get_gps_plugin_metrics()),
    #         self._options.console_gps_metrics.copy())
    #     gps_layout.update(self._make_key_value_table('GPS Module ' + formatted_plugin_status_str,
    #                                                  ui_filtered_gps_plugin_metrics,
    #                                                  border_style))
    #
    # if self._options.nmea_module and self._options.console_show_nmea_plugin:
    #     nmea_layout = Layout(name="nmea")
    #     # Populate the NMEA layout
    #     plugin_status = self._plugin_manager.get_nmea_plugin_status()
    #     formatted_plugin_status_str = self._get_formatted_plugin_status_str(plugin_status)
    #     border_style = self._get_border_style_from_status(plugin_status)
    #     ui_filtered_nmea_plugin_metrics = utils.get_filtered_key_value_list(
    #         utils.get_key_value_list(globals.NMEA_PLUGIN_METADATA_HEADERS,
    #                                  self._plugin_manager.get_nmea_plugin_metrics()),
    #         self._options.console_nmea_metrics.copy())
    #     nmea_layout.update(self._make_key_value_table('NMEA0183 Network ' + formatted_plugin_status_str,
    #                                                   ui_filtered_nmea_plugin_metrics,
    #                                                   border_style))

    data = {'curr_time': curr_time, 'victron_module': victron_module, 'battery_soc': battery_soc,
            'victron_status': victron_status, 'victron_status_colour': victron_status_colour,
            'fuel_tank': fuel_tank, 'water_tank': water_tank,
            'starter_battery_voltage': starter_battery_voltage, 'pv_max_power': pv_max_power, 'pv_power': pv_power,
            'active_input_source': active_input_source, 've_bus_state': ve_bus_state,
            'housing_battery_state': housing_battery_state, 'housing_battery_current': housing_battery_current,
            'pv_current': pv_current, 'status': status}
    return jsonify(data)
