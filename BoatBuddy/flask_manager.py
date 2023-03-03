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
from BoatBuddy.notifications_manager import NotificationsManager, NotificationEvents, NotificationEntryType
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

        webbrowser.open(f'http://{self._options.web_host}:{self._options.web_port}')
        app.run(debug=False, host=self._options.web_host, port=self._options.web_port)


def get_plugin_status_str(plugin_status: PluginStatus):
    plugin_status_str = ''
    if plugin_status == PluginStatus.DOWN:
        plugin_status_str = 'Down'
    elif plugin_status == PluginStatus.STARTING:
        plugin_status_str = 'Starting'
    elif plugin_status == PluginStatus.RUNNING:
        plugin_status_str = 'Running'
    return plugin_status_str


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

    return jsonify({})


@app.route('/data')
def get_data():
    curr_time = time.strftime("%H:%M:%S", time.localtime())
    status = application_modules.get_plugin_manager().get_status().value

    victron_module = False
    victron_status = ''
    active_input_source = 'N/A'
    ve_bus_state = 'N/A'
    housing_battery_state = 'N/A'
    housing_battery_current = 0
    pv_current = 0
    battery_soc = 0
    starter_battery_voltage = 0.0
    fuel_tank = 0
    water_tank = 0
    pv_max_configured_power = 0
    pv_power = 0
    if application_modules.get_options().victron_module:
        victron_module = True
        pv_max_configured_power = application_modules.get_options().victron_pv_max_power
        # Populate the victron layout
        plugin_status = application_modules.get_plugin_manager().get_victron_plugin_status()
        victron_status = get_plugin_status_str(plugin_status)
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

    nmea_module = False
    nmea_status = ''
    if application_modules.get_options().nmea_module:
        nmea_module = True
        plugin_status = application_modules.get_plugin_manager().get_nmea_plugin_status()
        nmea_status = get_plugin_status_str(plugin_status)

    gps_module = False
    gps_status = ''
    if application_modules.get_options().gps_module:
        gps_module = True
        plugin_status = application_modules.get_plugin_manager().get_gps_plugin_status()
        gps_status = get_plugin_status_str(plugin_status)

    # Collect session information
    session_name = ''
    start_time = ''
    start_time_utc = ''
    duration = ''
    start_gps_lat = ''
    start_gps_lon = ''
    distance = ''
    heading = ''
    average_wind_speed = ''
    average_wind_direction = ''
    average_water_temperature = ''
    average_depth = ''
    average_sog = ''
    average_sow = ''
    housing_battery_max_voltage = ''
    housing_battery_min_voltage = ''
    housing_battery_avg_voltage = ''
    housing_battery_max_current = ''
    housing_battery_avg_current = ''
    housing_battery_max_power = ''
    housing_battery_avg_power = ''
    pv_max_power = ''
    pv_avg_power = ''
    pv_max_current = ''
    pv_avg_current = ''
    starter_battery_max_voltage = ''
    starter_battery_min_voltage = ''
    starter_battery_avg_voltage = ''
    tank1_max_level = ''
    tank1_min_level = ''
    tank1_avg_level = ''
    tank2_max_level = ''
    tank2_min_level = ''
    tank2_avg_level = ''
    if application_modules.get_plugin_manager().get_status() == PluginManagerStatus.SESSION_ACTIVE:
        session_name = application_modules.get_plugin_manager().get_session_name()
        session_clock_metrics = application_modules.get_plugin_manager().get_session_clock_metrics()
        session_summary_metrics = application_modules.get_plugin_manager().get_session_summary_metrics()
        start_time = session_clock_metrics['Start Time (Local)']
        start_time_utc = session_clock_metrics['Start Time (UTC)']
        duration = session_clock_metrics['Duration']

        if application_modules.get_options().nmea_module:
            start_gps_lat = session_summary_metrics['[NM] Start GPS Lat (d°m\'S\" H)']
            start_gps_lon = session_summary_metrics['[NM] Start GPS Lon (d°m\'S\" H)']
            distance = session_summary_metrics['[NM] Dst. (miles)']
            heading = session_summary_metrics['[NM] Hdg. (°)']
            average_wind_speed = session_summary_metrics['[NM] Avg. Wind Speed (kts)']
            average_wind_direction = session_summary_metrics['[NM] Avg. Wind Direction (°)']
            average_water_temperature = session_summary_metrics['[NM] Avg. Water Temp. (°C)']
            average_depth = session_summary_metrics['[NM] Avg. Depth (m)']
            average_sog = session_summary_metrics['[NM] Avg. SOG (kts)']
            average_sow = session_summary_metrics['[NM] Avg. SOW (kts)']

        if application_modules.get_options().victron_module:
            housing_battery_max_voltage = session_summary_metrics['[GX] Batt. max voltage (V)']
            housing_battery_min_voltage = session_summary_metrics['[GX] Batt. min voltage (V)']
            housing_battery_avg_voltage = session_summary_metrics['[GX] Batt. avg. voltage (V)']
            housing_battery_max_current = session_summary_metrics['[GX] Batt. max current (A)']
            housing_battery_avg_current = session_summary_metrics['[GX] Batt. avg. current (A)']
            housing_battery_max_power = session_summary_metrics['[GX] Batt. max power (W)']
            housing_battery_avg_power = session_summary_metrics['[GX] Batt. avg. power (W)']
            pv_max_power = session_summary_metrics['[GX] PV max power (W)']
            pv_avg_power = session_summary_metrics['[GX] PV avg. power']
            pv_max_current = session_summary_metrics['[GX] PV max current (A)']
            pv_avg_current = session_summary_metrics['[GX] PV avg. current (A)']
            starter_battery_max_voltage = session_summary_metrics['[GX] Strt. batt. max voltage (V)']
            starter_battery_min_voltage = session_summary_metrics['[GX] Strt. batt. min voltage (V)']
            starter_battery_avg_voltage = session_summary_metrics['[GX] Strt. batt. avg. voltage']
            tank1_max_level = session_summary_metrics['[GX] Tank 1 max lvl']
            tank1_min_level = session_summary_metrics['[GX] Tank 1 min lvl']
            tank1_avg_level = session_summary_metrics['[GX] Tank 1 avg. lvl']
            tank2_max_level = session_summary_metrics['[GX] Tank 2 max lvl']
            tank2_min_level = session_summary_metrics['[GX] Tank 2 min lvl']
            tank2_avg_level = session_summary_metrics['[GX] Tank 2 avg. lvl']

    data = {'curr_time': curr_time, 'victron_module': victron_module, 'battery_soc': battery_soc,
            'victron_status': victron_status,
            'fuel_tank': fuel_tank, 'water_tank': water_tank,
            'starter_battery_voltage': starter_battery_voltage, 'pv_max_configured_power': pv_max_configured_power,
            'pv_power': pv_power,
            'active_input_source': active_input_source, 've_bus_state': ve_bus_state,
            'housing_battery_state': housing_battery_state, 'housing_battery_current': housing_battery_current,
            'pv_current': pv_current, 'status': status, 'nmea_module': nmea_module, 'nmea_status': nmea_status,
            'gps_module': gps_module, 'gps_status': gps_status, 'session_name': session_name, 'start_time': start_time,
            'start_time_utc': start_time_utc, 'duration': duration, 'start_gps_lat': start_gps_lat,
            'start_gps_lon': start_gps_lon, 'distance': distance, 'heading': heading,
            'average_wind_speed': average_wind_speed, 'average_wind_direction': average_wind_direction,
            'average_water_temperature': average_water_temperature, 'average_depth': average_depth,
            'average_sog': average_sog, 'average_sow': average_sow,
            'housing_battery_max_voltage': housing_battery_max_voltage,
            'housing_battery_min_voltage': housing_battery_min_voltage,
            'housing_battery_avg_voltage': housing_battery_avg_voltage,
            'housing_battery_max_current': housing_battery_max_current,
            'housing_battery_avg_current': housing_battery_avg_current,
            'housing_battery_max_power': housing_battery_max_power,
            'housing_battery_avg_power': housing_battery_avg_power,
            'pv_max_power': pv_max_power, 'pv_avg_power': pv_avg_power, 'pv_max_current': pv_max_current,
            'pv_avg_current': pv_avg_current, 'starter_battery_max_voltage': starter_battery_max_voltage,
            'starter_battery_min_voltage': starter_battery_min_voltage,
            'starter_battery_avg_voltage': starter_battery_avg_voltage,
            'tank1_max_level': tank1_max_level, 'tank1_min_level': tank1_min_level, 'tank1_avg_level': tank1_avg_level,
            'tank2_max_level': tank2_max_level, 'tank2_min_level': tank2_min_level, 'tank2_avg_level': tank2_avg_level,
            'last_notification': application_modules.get_notifications_manager().get_last_message()}
    return jsonify(data)
